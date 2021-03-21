import aiosqlite3
import ast
import asyncio
import datetime
import discord
import pyttsx3
from discord.ext import commands
from mojang import MojangAPI
from tabulate import tabulate

global green, red
green = 0x7ae19e
red = 0xdf4e4e


# import IdiotLibrary
# from IdiotLibrary import IdiotLib

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
        db = await aiosqlite3.connect('idiotbot.db')
        cursor = await db.execute(f'SELECT {select} FROM {table} {where}')
        rows = await cursor.fetchall()
        await cursor.close()
        await db.close()
        data = tabulate(rows, headers="keys", tablefmt='github')
        e = discord.Embed(title=f'SELECT {select} FROM {table} {where}',
        description=f'```py\n{data} ```', color=green)
        await ctx.send(embed=e)
        

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


def setup(client):
    print("Cog 'Other' Ready.")
    client.add_cog(Other(client))
