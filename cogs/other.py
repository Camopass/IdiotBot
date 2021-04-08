import aiosqlite3
import ast
import asyncio
import aiohttp
import datetime
import discord
import pyttsx3
import inspect
import datetime
import random
import traceback
import parsedatetime
import os
from discord.ext import commands
from mojang import MojangAPI
from tabulate import tabulate
from sqlite3 import OperationalError

import idiotlibrary
from idiotlibrary import green, red

'''
TODO

-- Add a user friendly datetime system.
-- Move tts to the music section.
-- Int to binary
-- translate
-- Syntax highlighting for ?view

'''

cal = parsedatetime.Calendar()

async def tts(text: str):
    engine = pyttsx3.init()
    engine.save_to_file(text, 'TTS.mp3')
    engine.runAndWait()


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@commands.command(hidden=True)
async def idiot(self, ctx, *, timestamp: str):
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    if timestamp.lower().startswith('on'):
        for month in months:
            if month in timestamp.lower():
                tmonth = months.index(month) + 1
                day = timestamp.lower().split(month)[1].replace(
                    'th', '').replace('st', '').replace('rd', '')
                day, year = day.split(',')
                day = day.strip(' ')
                year = year.strip(' ')
                print(day, tmonth, year)
                try:
                    year, arg = year.split(' ', maxsplit=2)
                except ValueError:
                    year = year.split(' ', maxsplit=2)[0]
                    arg = None
                break
        await ctx.send(f'{tmonth}, {day}, {year} : {arg}')
    if timestamp.lower().startswith('in'):
        days, months, years = (0, 0, 0)
        if 'days' in timestamp.lower():
            # in 3 days, 17 months, 7 years
            days = timestamp.lower().split(' days')[0]
            # in 3
            days = days.split(' ')
            days = days[len(days)-1]
            # 3
        if 'months' in timestamp.lower():
            # in 3 days, 17 months, 7 years
            months = timestamp.lower().split(' months')[0]
            # in 3 days, 17
            months = months.split(' ')
            months = months[len(months)-1]
            # 17
        if 'years' in timestamp.lower():
            # in 3 days, 17 months, 7 years
            years = timestamp.lower().split(' years')[0]
            # in 3 days, 17 months, 7
            years = years.split(' ')
            years = years[len(years)-1]
            # 7
        await ctx.send(f'{days}, {months}, {years}')

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        time = argument.split(':')
        hour = int(time[0])
        if time[1].lower().endswith('am'):
            time[1] = time[1].lower().replace('am', '')
        elif time[1].lower().endswith('pm'):
            hour += 12
            time[1] = time[1].lower().replace('pm', '')
        minute = int(time[1])
        return datetime.time(hour=hour, minute=minute)


class Other(commands.Cog):
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
            await tts(text)
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

    @commands.command(description='WIP: Does not work at the moment.')
    async def remind(self, ctx, event, *arg):
        args = arg
        if args is None:
            await ctx.send("Must pass arguments. I cannot understand that timestamp.")
        else:
            seconds = 0
            for argument in args:
                if argument.endswith("d"):
                    days = argument.split("d")[0]
                    seconds += int(days) * 86400
                if argument.endswith("h"):
                    hours = argument.split("h")[0]
                    seconds += int(hours) * 3600
                if argument.endswith("m"):
                    minutes = argument.split("m")[0]
                    seconds += int(minutes) * 60
                if argument.endswith("s"):
                    seconds2 = argument.split("s")[0]
                    seconds += int(seconds2)
            time = datetime.timedelta(seconds=seconds) + datetime.datetime.now()
            async with aiosqlite3.connect('idiotbot.db') as db:
                await db.execute('INSERT INTO reminders VALUES (?, ?, ?, ?)', (ctx.author.id, event, str(time), ctx.channel.id))
                await db.commit()
            h_time = time.strftime('%A the %d, %B, %Y at %H:%M')
            return await ctx.send (
                embed=discord.Embed (
                    title=f'Event scheduled to be on {h_time}',
                    description=f'Event: `{event}`',
                    color=green
                )
            )


    @commands.command(name='eval', hidden=True)
    @commands.is_owner()
    async def eval_fn(self, ctx, *, cmd):
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = (await eval(f"{fn_name}()", env))
            await ctx.send(result)
        except Exception as e:
            await ctx.send(embed=discord.Embed(title='Error', description=f'''Error:
```{e}```''', color=0x7ae19e))

    # @eval_fn.error()
    # async def eval_error(self, ctx, error):
    #    e = discord.Embed(title='Error', description='You must be the owner of the bot to use this command.', color=red)
    #    await ctx.send(embed=e)

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
    
    @commands.group(hidden=True)
    async def time(self, ctx):
        pass

    @time.command()
    async def subtract(self, ctx, time0:TimeConverter, time1:TimeConverter):
        await ctx.send(time1 - time0)


def setup(client):
    client.add_cog(Other(client))

if __name__ == '__main__':
    os.system(
        r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:/workspace/idiotbot/idiot bot.py"')
