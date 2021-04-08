import asyncio
import os
import discord
import youtube_dl
from discord.ext import commands, menus

global queue
queue = {}

import idiotlibrary
from idiotlibrary import red, green, trim_str

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


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def do_play(ctx, self, player_menu):
    if ctx.voice_client:
        player = await YTDLSource.from_url(queue[ctx.guild.id][0], loop=self.bot.loop, stream=False)
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
                                player = await YTDLSource.from_url(queue[ctx.guild.id][0], loop=self.bot.loop, stream=False)
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
        except AttributeError:
            pass
    else:
        raise RuntimeError('Bot is not connected to voice channel.')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def joinvc(self, channel, vc):
        if vc is not None:
            return await vc.move_to(channel)
        await channel.connect()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await guild.me.edit(deafen=True)

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
        # if len(queue) == 0:
        if url is None:
            ctx.voice_client.resume()
            await ctx.message.add_reaction("\U0001f44d")
        else:
            if ctx.voice_client.is_playing():
                if ctx.guild.id in queue.keys():
                    async with ctx.typing():
                        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                        queue[ctx.guild.id].append(player.title)
                        embed = discord.Embed(title=f"Queued **{player.title}**",
                                              description=f"Queued: **[{player.title}]({player.url})** ({convert(player.length)})",
                                              color=green)
                        embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=str(ctx.author.avatar_url))
                        embed.set_thumbnail(url=player.thumb)
                        embed.set_footer(text=f'By: {player.author} • {player.likes} likes')
                        return await ctx.send(embed=embed)
            channel = ctx.message.author.voice.channel
            await self.joinvc(channel, ctx.voice_client)
            member = ctx.guild.me
            await member.edit(deafen=True)
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
                if not ctx.guild.id in queue.keys():
                    queue[ctx.guild.id] = [player.title]
                if len(queue[ctx.guild.id]) == 0:
                    queue[ctx.guild.id] = [player.title]
                #ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            embed = Embed(player, ctx.author)
            #await ctx.send(embed=embed.embed)
            menu = PlayerMenu(embed.embed, ctx.voice_client)
            await menu.start(ctx)
            await do_play(ctx, self, menu)
            


    @commands.command()
    async def queue(self, ctx):
        if ctx.guild.id in queue.keys():
            if len(queue[ctx.guild.id]) != 0:
                q = []
                for song in queue[ctx.guild.id]:
                    s = trim_str(song, 25)
                    if len(song) > 25:
                        s += '...'
                    sp_count = 36 - len(s)
                    s += ''.join(' ' for x in range(sp_count))
                    s += '|'
                    q.append(s)
                lis = '\n'.join(q)
                await ctx.send(embed=discord.Embed(title='Queue', description=f'```{lis}```', color=green))
            else:
                await ctx.send('Queue is empty. Use ?play [song] to add a song to the queue.')
        else:
            await ctx.send('Queue is empty. Use ?play [song] to add a song to the queue.')


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


def setup(client):
    client.add_cog(Music(client))


if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:/workspace/idiotbot/idiot bot.py"')
