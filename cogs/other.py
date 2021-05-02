import aiosqlite3
import asyncio
import aiohttp
import datetime
import discord
import pyttsx3
import inspect
import datetime
import random
import os
from discord.ext import commands
from mojang import MojangAPI
from tabulate import tabulate
from sqlite3 import OperationalError
from io import BytesIO
import idiotlibrary
from idiotlibrary import green, red, name


'''
TODO

-- Move tts to the music section.
-- Int to binary
-- translate
-- Syntax highlighting for ?view

'''

async def tts(text: str):
    engine = pyttsx3.init()
    engine.save_to_file(text, 'TTS.mp3')
    engine.runAndWait()


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        time = argument.split(':')
        hour = int(time[0])
        if time[1].lower().endswith('am'):
            time[1] = time[1].lower().replace('am', '').strip(' ')
        elif time[1].lower().endswith('pm'):
            hour += 12
            time[1] = time[1].lower().replace('pm', '').strip(' ')
        minute = int(time[1])
        return datetime.timedelta(hours=hour, minutes=minute)


def get_all_emotes(bot):
    result = []
    for guild in bot.guilds:
        for emote in guild.emojis:
            result.append(emote)

    return result



class other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(description='Send a message using text-to-speech robot voice. Use {0}tts [Voice Channel] [Message]')
    async def tts(self, ctx, vc: discord.VoiceChannel = None, *, text: str):
        if vc is None:
            e = discord.Embed(title="Error",
                                description="You have to have a voice channel you moron. Like this: ?TTS General Message",
                                color=red)
            await ctx.send(embed=e)
            return
        if len(text) >= 401:
            e = discord.Embed(title="Error", description="Message Must be 400 or Fewer in Length.", color=red)
            await ctx.send(embed=e)
        else:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            message = await ctx.send(embed=discord.Embed(title="Creating TTS...",
                                                            description=f"Making TTS MP3 File for message: ```{text}```",
                                                            color=green))
            await tts(f'{name(ctx.author)} said: {text}')
            await asyncio.sleep(1)
            e = discord.Embed(title="MP3 File Created Successfully",
                                description=f"Successfuly created the TTS MP3 File for the message: ```{text}```",
                                color=green)
            await message.edit(embed=e)
            player = discord.FFmpegPCMAudio("TTS.mp3")
            await vc.connect()
            ctx.voice_client.play(player)
            await asyncio.sleep(180)
            if ctx.voice_client.is_playing():
                pass
            else:
                await ctx.voice_client.disconnect()
    

    @commands.command(description='Use {0}choose and then have all of the choices you want to choose from. The choices are separated by spaces. You can add quotes around the option to keep it as once.')
    async def choose(self, ctx, *choices):
        await ctx.send(random.choice(choices))
    

    @commands.command(description='View the source code for a command. Use {0}source [command], or {0}source for a link to the github page.')
    async def source(self, ctx, command=None):
        if command is None:
            return await ctx.send('My full source code is available at https://github.com/Camopass/IdiotBot')
        else:
            for _, cog in self.bot.cogs.items():
                commands = cog.get_commands()
                for command_ in commands:
                    if command == command_.name:
                        source = inspect.getsource(
                            command_.callback).replace('```', '\'\'\'')
                        if len(source) < 1500:
                            return await ctx.send(f'```py\n{source}```')
                        else:
                            return await idiotlibrary.pages_simple(ctx, source, prefix='```py')
            await ctx.send('Could not find that command.')
    

    @commands.command(description='Convert binary to a decimal integer.')
    async def binary(self, ctx, b: str):
        r = 0
        for index, i in enumerate(b):
            r += int(i) * (2 ** (len(b) - index - 1))
        await ctx.send(r)
    

    @commands.command(description='Suggest a feature for the bot. I will not be adding slash commands, or the "/" prefix, as those commands suck.')
    async def suggest(self, ctx, *, suggestion):
        channel = self.bot.get_channel(813451902774673468)
        e = discord.Embed(
            title=f'Suggestion by *{ctx.author.id}*', description=suggestion, color=green)
        await ctx.send(embed=e)
        msg = await channel.send(embed=e)
        await msg.add_reaction('\U00002705')
        await msg.add_reaction('\U0000274c')
    

    @commands.group()
    async def emotes(self, ctx):
        emotes = get_all_emotes(ctx.bot)
        limit = 10
        if len(emotes) > limit:
            emotes = emotes[0:limit]
        emotes = [(str(emoji) + ' :' + emoji.name + ':') for emoji in emotes]
        emotes = idiotlibrary.trim_str(' \n'.join(emotes))
        e = discord.Embed(title='Available Emotes', description=emotes, color=green)
        await ctx.send(embed=e)
    

    @commands.command()
    async def botinfo(self, ctx):
        e = discord.Embed(title=f'Info for: **{self.bot.user.name}**',
                        description=f'Information for Stupid Idiot Bot. Stupid Idiot Bot has been in development for: **{(datetime.date.today() - datetime.date(year=2020, month=12, day=31)).days}** days.',
                        color=green)
        e.add_field(name='Commands',
                    value=f'{self.bot.user.name} has **{len(self.bot.commands)}** commands.')
        members = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if not member in members:
                    members.append(member)
        e.add_field(name='Servers',
                    value=f'{self.bot.user.name} is in **{len(self.bot.guilds)}** servers and can see **{len(members)}** users.')
        await ctx.send(embed=e)
    

    @commands.command(aliases=['serverinfo'])
    async def guildinfo(self, ctx):
        created_at = datetime.datetime.now() - ctx.guild.created_at
        e = discord.Embed(title=ctx.guild.name,
         description=f'The server **{ctx.guild.name}** was created {str(created_at.days)} days ago.',
         color=green)
        e.add_field(name='Owner', value=ctx.guild.owner.mention)
        e.add_field(name='Channels', value=str(len(ctx.guild.channels)) + ' channels.', inline=False)
        e.add_field(name='Emojis', value=str(len(ctx.guild.emojis)) + ' emojis.', inline=False)
        e.add_field(name='Members', value=str(ctx.guild.member_count) + ' members.', inline=False)
        e.add_field(name='Roles', value=str(len(ctx.guild.roles)) + ' roles.', inline=False)
        if ctx.guild.banner:
            e.set_image(url=ctx.guild.banner)
        e.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=e)


    @commands.command(description='WIP: Does not work at the moment.')
    async def remind(self, ctx, event, *, time:idiotlibrary.SimpleTimeDelta=None):
        if time is None:
            await ctx.send("Must pass arguments. I cannot understand that timestamp.")
        if datetime.datetime.now() - time > datetime.timedelta(seconds=0):
            await ctx.send('That time is in the past.')
        else:
            async with aiosqlite3.connect('idiotbot.db') as db:
                await db.execute('INSERT INTO reminders VALUES (?, ?, ?, ?)', (ctx.author.id, event, str(time), ctx.channel.id))
                await db.commit()
            h_time = time.strftime('%A the %d of %B, %Y at %H:%M:%S')
            return await ctx.send (
                embed=discord.Embed (
                    title=f'Event scheduled to be on {h_time}',
                    description=f'Event: `{event}`',
                    color=green
                )
            )


    @commands.command(hidden=True)
    @commands.is_owner()
    async def select(self, ctx, select, table, *, where=""):
        try:
            db = await aiosqlite3.connect('idiotbot.db')
            cursor = await db.execute(f'SELECT {select} FROM {table} {where}')
            rows = await cursor.fetchall()
            names = await db.execute(f'PRAGMA table_info({table})')
            n = []
            for _, name, _, _, _, _ in names:
                n.append(name)
            await cursor.close()
            await db.close()
            data = tabulate(rows, headers=n, tablefmt='github')
            e = discord.Embed(title=f'SELECT {select} FROM {table} {where}',
            description=f'```py\n{data} ```', color=green)
            await ctx.send(embed=e)
        except OperationalError:
            await ctx.send('Could not find that table.')
            if db:
                await db.close()
        

    @commands.command(description='Use {0}skin [Minecraft Username] to retrieve the skin of that user. Sometimes it might take a while to update, so beware of that. It is a glitch with discord, not the bot.')
    async def skin(self, ctx, *, user: str):
        uuid = MojangAPI.get_uuid(user)
        if uuid is None:
            embed = discord.Embed(
                title="Error", description="User does not exist.", color=0xdf4e4e)
            await ctx.send(embed=embed)
        else:
            skin = f"https://crafatar.com/avatars/{uuid}?overlay"
            render = f"https://crafatar.com/renders/body/{uuid}?overlay"
            e = discord.Embed(title=f"{user} (Click Here to get Download)",
                              description=f"UUID: {uuid}", color=0x7ae19e, url=f"https://crafatar.com/skins/{uuid}")
            e.set_thumbnail(url=skin)
            e.set_image(url=render)
            await ctx.send(embed=e)


    @commands.command(hidden=True)
    async def days_until(self, ctx, day=datetime.date(year=2021, month=5, day=26)):
        await ctx.send(str(day - datetime.date.today()))
    

    @commands.command(description='Attach a .txt file to this message and the bot will send a viewing menu for the .txt file.')
    async def view(self, ctx):
        if len(ctx.message.attachments) > 0:
            file_ = ctx.message.attachments[0]
            content = await file_.read()
            content = str(content, 'utf-8')
            if len(content) >= 1994:
                content = content.replace('```', '\'\'\'')
                await idiotlibrary.pages_simple(ctx, content)
            else:
                content = content.replace('```', '\'\'\'')
                await ctx.send(f'```{content}```')
    

    @commands.group(invoke_without_command=True, description='Get an invite to invite Stuipid Idiot Bot to your server!')
    async def invite(self, ctx):
        e = discord.Embed(title='Invite',
                          description= '\n'.join([
                          '[General Invite](https://discord.com/api/oauth2/authorize?client_id=478709969152376832&permissions=1039526982&scope=bot)',
                          '[Minimal Invite](https://discord.com/api/oauth2/authorize?client_id=478709969152376832&permissions=674622016&scope=bot)',
                          '[Admin Invite](https://discord.com/api/oauth2/authorize?client_id=478709969152376832&permissions=8&scope=bot)'
                          ]),
                          color=green
        )
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_footer(text='Made by Monke Man#7861',
                     icon_url=self.bot.get_user(379307644730474496).avatar_url)
        await ctx.send(embed=e)
    

    @invite.command(name='general', description='General Invite URL')
    async def invite_general(self, ctx):
        e = discord.Embed(title='General Invite URL', color=green,
                          url='https://discord.com/api/oauth2/authorize?client_id=478709969152376832&permissions=1039526982&scope=bot')
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_footer(text='Made by Monke Man#7861',
                     icon_url=self.bot.get_user(379307644730474496).avatar_url)
        await ctx.send(embed=e)
    

    @invite.command(name='minimal', description='Minimal permissions invite URL')
    async def invite_minimal(self, ctx):
        e = discord.Embed(title='Minimal Invite URL', color=green,
                          url='https://discord.com/api/oauth2/authorize?client_id=478709969152376832&permissions=674622016&scope=bot')
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_footer(text='Made by Monke Man#7861',
                     icon_url=self.bot.get_user(379307644730474496).avatar_url)
        await ctx.send(embed=e)
    

    @invite.command(name='admin', description='Admin permissions invite URL')
    async def invite_admin(self, ctx):
        e = discord.Embed(title='Admin Invite URL', color=green,
                          url='https://discord.com/api/oauth2/authorize?client_id=478709969152376832&permissions=8&scope=bot')
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_footer(text='Made by Monke Man#7861',
                     icon_url=self.bot.get_user(379307644730474496).avatar_url)
        await ctx.send(embed=e)
    

    @commands.group(description='Time commands')
    async def time(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(title=datetime.datetime.now().strftime('%I:%M:%S %p on %A the %d of %B, %Y').lstrip('0'), color=green))


    @time.command(name='subtract', description='Subtract two times in the format hh:mm')
    async def time_subtract(self, ctx, time1:TimeConverter, time0:TimeConverter):
        await ctx.send(time1 - time0)
    
    
    @time.command(name='add', description='Add two times together with the format hh:mm')
    async def time_add(self, ctx, time1:TimeConverter, time0:TimeConverter):
        await ctx.send(time0 + time1)
    

    @time.command(name='in', description='Displays the time it will be in the specified time. Use the format HH:MM. You can also use am and pm.')
    async def time_in(self, ctx, *, time:TimeConverter):
        await ctx.send((datetime.datetime.now() + time).strftime('%I:%M:%S %p on %A the %d of %B, %Y').lstrip('0'))
    

    @time.command(name='until', description='Displays the time until a specified time. Use the format HH:MM. You can also use am and pm.')
    async def time_until(self, ctx, *, time:TimeConverter):
        now = datetime.datetime.now()
        t = datetime.timedelta(hours=now.hour, seconds=now.second, minutes=now.minute)
        t = time - t
        await ctx.send(str(t))



def setup(client):
    client.add_cog(other(client))



if __name__ == '__main__':
    os.system(
        r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:/workspace/idiotbot/idiot bot.py"')
