import asyncio
import os
import discord
import youtube_dl
import datetime
import aiosqlite3
import datetime
import math
from discord.ext import commands, menus

global queue
queue = {}

import idiotlibrary
from idiotlibrary import red, green, trim_str

databasedir = 'idiotbot.db'

'''
TODO:

-- Make sure playlists work like they are supposed to.
-- Try to get spotify working. 
-- Looping.
-- More queue options.

'''


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class PlayerError(Exception):
    pass


class PlayerMenu(menus.Menu):
    def __init__(self, embed:discord.Embed, voice_client):
        super().__init__()
        self.embed = embed
        self.client = voice_client

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=self.embed)

    @menus.button('\U000023f8')
    async def on_play(self, payload):
        self.client.pause()

    @menus.button('\U000025b6')
    async def on_pause(self, payload):
        self.client.resume()
    
    @menus.button('\U000023e9')
    async def on_next(self, payload):
        self.client.stop()

    @menus.button('\U000023f9')
    async def on_stop(self, payload):
        await self.client.disconnect()
        self.stop()
        await self.message.clear_reactions()
        queue[self.ctx.guild.id] = []


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.length = data.get('duration')
        self.title = data.get('title')
        self.url = data.get('webpage_url')
        self.thumb = data.get('thumbnail')
        self.author = data.get('uploader')
        self.likes = data.get('like_count')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            try:
                data = data['entries'][0]
            except IndexError:
                filename = data['url'] if stream else ytdl.prepare_filename(data)
                return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Embed:
    def __init__(self, player, author):
        embed = discord.Embed(title=f"Now playing **{player.title}**",
                              description=f"Playing: **[{player.title}]({player.url})** ({convert(player.length)})",
                              color=green)
        embed.set_author(
            name=f'Requested by {author.name}', icon_url=str(author.avatar_url))
        embed.set_thumbnail(url=player.thumb)
        embed.set_footer(
            text=f'By: {player.author} • {player.likes} likes')
        self.embed = embed


class AlreadyQueued(Exception):
    pass


class Song:
    def __init__(self, channel_id:int, guild_id:int, author_id:int,
    song_name:str, song_url:str, song_author:str, song_likes:int,
    song_length:str, started_at:str, queue_id:int):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.author_id = author_id
        self.song_name = song_name
        self.url = song_url
        self.song_author = song_author
        self.song_likes = song_likes
        self.song_length = song_length
        self.started_at = started_at
        self.length_delta = datetime.timedelta(seconds=self.song_length)
        self.id = id(self.url)
        self.queue_id = queue_id
    
    def __str__(self):
        return self.song_name

    def __len__(self):
        return math.ceil(self.song_length)
    
    def __ge__(self, other):
        return self.song_length >= other.song_length

    def __le__(self, other):
        return self.song_length <= other.song_length
    
    def __lt__(self, other):
        return self.song_length < other.song_length
    
    def __ne__(self, other):
        return self.url != other.url
    
    def __eq__(self, other):
        return self.url == other.url
    
    def __add__(self, other):
        return self.song_length + other.song_length
    
    async def save(self):
        async with aiosqlite3.connect(databasedir) as db:
            await db.execute('INSERT INTO queues VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (self.channel_id,
            self.guild_id, self.author_id, self.song_name, self.url, self.song_author, self.song_likes, self.song_length, self.queue_id))
            await db.commit()
    
    async def length_as_timedelta(self):
        return datetime.timedelta(seconds=self.song_length)


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


async def do_play(ctx, self, player_menu):
    if ctx.voice_client:
        player = await YTDLSource.from_url(queue[ctx.guild.id][0].url, loop=self.bot.loop, stream=False)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        try:
            while ctx.voice_client.is_connected():
                if ctx.voice_client.is_playing() == False and not ctx.voice_client.is_paused():
                    if len(queue[ctx.guild.id]) == 0:
                        await ctx.voice_client.disconnect()
                        return
                    else:
                        queue[ctx.guild.id].pop(0)
                        async with ctx.typing():
                            if len(queue[ctx.guild.id]) != 0:
                                player = await YTDLSource.from_url(queue[ctx.guild.id][0].url, loop=self.bot.loop, stream=False)
                                ctx.voice_client.play(player, after=lambda e: print(
                                    'Player error: %s' % e) if e else None)
                                embed = Embed(player, ctx.author)
                                player_menu.stop()
                                await player_menu.message.clear_reactions()
                                player_menu = PlayerMenu(embed.embed, ctx.voice_client)
                                await player_menu.start(ctx)
                            else:
                                player_menu.stop()
                                await player_menu.message.clear_reactions()
                                await ctx.voice_client.disconnect()
                await asyncio.sleep(0.1)
            queue[ctx.guild.id] = []
        except AttributeError:
            pass
    else:
        raise RuntimeError('Bot is not connected to voice channel.')

'''


async def run_queue(self, ctx, queue:Queue):
    if ctx.voice_client is None or ctx.voice_client.is_connected() == False:
        raise PlayerError('Voice Client not found.')
    song = queue.queue[queue.is_on]
    async with ctx.typing():
        player = await YTDLSource.from_url(song.url, loop=self.bot.loop, stream=False)
        ctx.voice_client.play(player, after=lambda e: print(
            'Player Error: %s' % e) if e else None)
    e = Embed(player, ctx.author)
    await ctx.send(embed=e.embed)
    while ctx.voice_client.is_connected():
        if ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            ctx.voice_client.stop()
            song = queue.next()
            async with ctx.typing():
                player = await YTDLSource.from_url(song.url, loop=self.bot.loop, stream=False)
                ctx.voice_client.play(player, after=lambda e: print(
                    'Player Error: %s' % e) if e else None)
            e = Embed(player, ctx.author)
            await ctx.send(embed=e.embed)
            return
        else:
            pass'''


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def joinvc(self, channel, vc):
        if vc is not None:
            return await vc.move_to(channel)
        await channel.connect()


    @commands.command(aliases=["j", "connect"])
    async def join(self, ctx):
        if not ctx.message.author.voice:
            embed = discord.Embed(title="Error", description="Please connect to a voice channel.", color=0xc2af38)
            await ctx.send(embed=embed)
            return
        else:
            channel = ctx.message.author.voice.channel
            await self.joinvc(channel, ctx.voice_client)
            member = ctx.guild.me
            await member.edit(deafen=True)


    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url: str = None):
        if url is None:
            ctx.voice_client.resume()
            await ctx.message.add_reaction("\U0001f44d")
        else:
            if ctx.voice_client.is_playing():
                if ctx.guild.id in queue.keys():
                    async with ctx.typing():
                        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                        song = Song(ctx.channel.id, ctx.guild.id, ctx.author.id, player.title, player.url, player.author, player.likes, player.length, datetime.datetime.now(), id(str(ctx.author.id) + str(ctx.guild.id)))
                        queue[ctx.guild.id].append(song)
                        embed = discord.Embed(title=f"Queued **{player.title}**",
                                              description=f"Queued: **[{player.title}]({player.url})** ({convert(player.length)})",
                                              color=green)
                        embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=str(ctx.author.avatar_url))
                        embed.set_thumbnail(url=player.thumb)
                        embed.set_footer(text=f'By: {player.author} • {player.likes} likes')
                        return await ctx.send(embed=embed)
            channel = ctx.message.author.voice.channel
            await self.joinvc(channel, ctx.voice_client)
            try:
                member = ctx.guild.me
                await member.edit(deafen=True)
            except discord.errors.Forbidden:
                await ctx.send('Could you please deafen me? It helps make the bot faster and better.')
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
                if not ctx.guild.id in queue.keys():
                    song = song = Song(ctx.channel.id, ctx.guild.id, ctx.author.id, player.title, player.url, player.author,
                                       player.likes, player.length, datetime.datetime.now(), id(str(ctx.author.id) + str(ctx.guild.id)))
                    queue[ctx.guild.id] = [song]
                if len(queue[ctx.guild.id]) == 0:
                    song = song = Song(ctx.channel.id, ctx.guild.id, ctx.author.id, player.title, player.url, player.author,
                                       player.likes, player.length, datetime.datetime.now(), id(str(ctx.author.id) + str(ctx.guild.id)))
                    queue[ctx.guild.id] = [song]
                #ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            embed = Embed(player, ctx.author)
            #await ctx.send(embed=embed.embed)
            menu = PlayerMenu(embed.embed, ctx.voice_client)
            await menu.start(ctx)
            await do_play(ctx, self, menu)
    

    '''
    @commands.command(aliases=['p'])
    async def play(self, ctx, *, song:str=None):
        if song is None:
            if ctx.voice_client != None:
                if (not ctx.voice.is_playing()) and ctx.voice_client.is_connected():
                    ctx.voice_client.resume()
        else:
            if ctx.voice_client != None:
                async with aiosqlite3.connect(databasedir) as db:
                    c = await db.execute('SELECT * FROM QueueID WHERE guild_id=?', (ctx.guild.id,))
                    if c is None:
                        qid = id(str(ctx.author.id)+str(ctx.author.id))
                        async with ctx.typing():
                            player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=False)
                        song = Song(ctx.channel.id, ctx.guild.id, ctx.author.id, player.name, player.url,
                        player.author, player.likes, player.length, datetime.datetime.now(), qid)
                        q = Queue(ctx.author.id, ctx.guild.id, [song])
                        await db.execute('INSERT INTO QueueID VALUES (?, ?)', (ctx.guild.id, qid))
                        await db.commit()
                        await q.save()
                        await run_queue(self, ctx, q)
                    if ctx.voice_client.is_connected() and ctx.voice_client.is_playing():
                        c = await db.execute('SELECT queue_id FROM QueueID WHERE guild_id=?', (ctx.guild.id,))
                        queue_id, = await c.fetchone()
                        c = await db.execute('SELECT * FROM queues WHERE queue_id=?', (queue_id,))

            player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=False)
            song = Song(ctx.channel.id, ctx.guild.id, ctx.author.id, player.title, player.url,
                        player.author, player.likes, player.length, datetime.datetime.now(), id(str(ctx.author.id)+str(ctx.author.id)))
    '''


    @commands.command()
    async def queue(self, ctx):
        if ctx.guild.id in queue.keys():
            if len(queue[ctx.guild.id]) != 0:
                q = []
                for song in queue[ctx.guild.id]:
                    s = trim_str(song.song_name, 25)
                    if len(song.song_name) > 25:
                        s += '...'
                    sp_count = 30 - len(s)
                    s += ''.join(' ' for x in range(sp_count))
                    s += f'| {convert(len(song))}'
                    q.append(s)
                lis = '\n'.join(q)
                totalen = [await s.length_as_timedelta() for s in queue[ctx.guild.id]]
                l = datetime.timedelta(seconds=0)
                for length in totalen:
                    l = l + length
                length = convert(l.total_seconds())
                await ctx.send(embed=discord.Embed(title='Queue', description=f' {l} ```{lis}```', color=green))
            else:
                await ctx.send(f'Queue is empty. Use {ctx.prefix}play [song] to add a song to the queue.')
        else:
            await ctx.send(f'Queue is empty. Use {ctx.prefix}play [song] to add a song to the queue.')
    

    @commands.command(aliases=['playing', 'current'])
    async def now(self, ctx):
        if ctx.guild.id in queue.keys():
            if len(queue[ctx.guild.id]) != 0:
                now = datetime.datetime.now()
                song = queue[ctx.guild.id][0]
                time_left = song.length_delta - (now - song.started_at)
                e = discord.Embed(title=song.song_name,
                description=f'Requested by <@{song.author_id}> • {convert(time_left.total_seconds())} left',
                color=green,
                url=song.url)
                e.set_footer(text=f'By {song.song_author} • {song.song_likes} likes')
                await ctx.send(embed=e)
    

    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        ctx.voice_client.stop()
        await ctx.message.add_reaction('\U0001f44d')


    @commands.command(aliases=["loudness", "v"])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        if volume > 100:
            await ctx.send("No. You can't set the volume to be greater than 100.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"\U0001f44d Volume is now {volume}%")


    @commands.command(aliases=["leave", "disconnect"])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()


    @commands.command()
    async def pause(self, ctx):
        ctx.voice_client.pause() 
        await ctx.message.add_reaction("\U0001f44d")


    @commands.command()
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.message.add_reaction("\U0001f44d")


    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")


def setup(bot):
    bot.add_cog(music(bot))


if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:/workspace/idiotbot/idiot bot.py"')
