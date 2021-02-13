import asyncio, time, datetime
import discord, json, sqlite3
import youtube_dl

from discord.ext import commands

global c
global conn
conn = sqlite3.connect('idiotbot.db')
c = conn.cursor()

global queue
queue = []

# Suppress noise about console usage from errors
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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

#def convertToDateTime


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.length = data.get('duration')
        self.title = data.get('title')
        self.url = data.get('url')
        self.thumb = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)

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
    async def play(self, ctx, *, url:str=None):
        #if len(queue) == 0:
        queue.append(url)
        if url == None:
            await ctx.voice_client.resume()
            await ctx.send("\U0001f44d Resumed")
        else:
            channel = ctx.message.author.voice.channel
            await self.joinvc(channel, ctx.voice_client)
            member = ctx.guild.me
            await member.edit(deafen=True)
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            embed = discord.Embed(title=f"Now playing **{player.title}**", description=f"Playing: **{player.title}** ({convert(player.length)})", color=0xc2af38)
            embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=str(ctx.author.avatar_url))
            embed.set_thumbnail(url=player.thumb)
            await ctx.send(embed=embed)
            del queue[ctx.guild.id][0]
        '''else:
            queue.append(url)
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
            await ctx.send(f"Song `{player.title}` appended to the queue. Use ?queue to see the queue.")'''

    @commands.command()
    async def queue(self, ctx):
        try:
            q = queue[ctx.guild.id]
            await ctx.send(q)
        except:
            queue[ctx.guild.id] = []
            await ctx.send("Queue is empty.")


    @commands.command(aliases=["loudness", "v"])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        if volume >> 100:
            await ctx.send("No. You can't set the volume to be greater than 100.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"\U0001f44d Volume is now {volume}%")

    @commands.command(aliases=["leave", "disconnect"])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send("\U0001f44d Paused")

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("\U0001f44d Resumed")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.command(description= 'Remind you about a specified event a certain amount of minutes later.', brief= "Set a reminder.")
    async def remindl(self, ctx, minutes: str, *, event: str):
        try:
            if minutes.endswith("m"):
                f = "minutes"
                time = int(minutes[:-1]) * 60
            elif minutes.endswith("s"):
                f = "seconds"
                time = int(minutes[:-1])
            elif minutes.endswith("d"):
                f = "days"
                time = int(minutes[:-1]) * 86400
            elif minutes.endswith("h"):
                f = "hours"
                time = int(minutes[:-1]) * 3600
            else:
                f = None
                await ctx.send("Invalid format. Please use one of the suffixes 's' (seconds), 'm' (minutes), or 'd' (days). (You can only use one of these.)")
                return
            if time >> 259200:
                await ctx.send("The amount of time must be under three days.")
            elif f != None:
                embed=discord.Embed(title=f"Event **{event}**", description=f'Scheduled to be in **{minutes[:-1]}** {f}.', color=0xc2af38)
                embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=str(ctx.author.avatar_url))
                await ctx.send(embed= embed)
                #await ctx.send(f'Event {event} has been scheduled to be in {minutes} minutes.')
                await asyncio.sleep(time)
                embed=discord.Embed(title=f"Event **{event}**", description=f"Time's up, {ctx.author.mention}", color=0xc2af38)
                embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=str(ctx.author.avatar_url))
                await ctx.send(content= str(ctx.author.mention), embed= embed)
        except:
            pass
            #I know it works it just gives me an error



def setup(client):
    print("Cog 'Music' Ready.")
    client.add_cog(Music(client))
