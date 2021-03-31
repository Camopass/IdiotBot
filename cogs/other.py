import aiosqlite3
import ast
import asyncio
import datetime
import discord
import pyttsx3
import inspect
import datetime
from discord.ext import commands
from mojang import MojangAPI
from tabulate import tabulate
from sqlite3 import OperationalError

import idiotlibrary
from idiotlibrary import green, red

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

    @commands.command()
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
    
    @commands.command()
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
    
    @commands.command()
    async def binary(self, ctx, b: str):
        r = 0
        for index, i in enumerate(b):
            r += int(i) * (2 ** (len(b) - index - 1))
        await ctx.send(r)
    
    @commands.command()
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
        e = discord.Embed(title=f'Info for: **{client.user.name}**',
                        description=f'Information for Stupid Idiot Bot. Stupid Idiot Bot has been in development for: **{(datetime.date.today() - datetime.date(year=2020, month=12, day=31)).days}** days.',
                        color=green)
        e.add_field(name='Commands',
                    value=f'{client.user.name} has **{len(client.commands)}** commands.')
        members = []
        for guild in client.guilds:
            for member in guild.members:
                if not member in members:
                    members.append(member)
        e.add_field(name='Servers',
                    value=f'{client.user.name} is in **{len(client.guilds)}** servers and can see **{len(members)}** users.')
        await ctx.send(embed=e)

    @commands.command()
    async def remind(self, ctx, *arg):
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
            await ctx.send(str(datetime.timedelta(seconds=seconds)))
            await ctx.send(str(datetime.timedelta(seconds=seconds) + datetime.datetime.now()))

    @commands.command(name='eval')
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

    @commands.command()
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
        

    @commands.command()
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

    @commands.command()
    async def days_until(self, ctx, day=datetime.date(year=2021, month=5, day=26)):
        await ctx.send(str(day - datetime.date.today()))
    
    @commands.command()
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
    
    @commands.group()
    async def time(self, ctx):
        pass

    @time.command()
    async def subtract(self, ctx, time0:TimeConverter, time1:TimeConverter):
        await ctx.send(time1 - time0)


def setup(client):
    client.add_cog(Other(client))
