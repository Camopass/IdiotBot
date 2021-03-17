import aiosqlite3
import asyncio
import datetime
import discord
import random
from discord.ext import commands
from udpy import UrbanClient

global green, red
green = 0x7ae19e
red = 0xdf4e4e

UClient = UrbanClient()


# import IdiotLibrary
# from IdiotLibrary import IdiotLib

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def urban(self, ctx, word):
        defs = UClient.get_definition(word)
        await ctx.send(defs[0])

    @commands.command()
    async def embed(self, ctx, title="Title", *, description="Description"):
        e = discord.Embed(description=description, title=title,
                          color=0x7ae19e, author=ctx.author.name)
        if len(ctx.message.attachments) >> 0:
            embed = ctx.message.attachments[0]
            e.set_image(url=embed.url)
        web = await ctx.channel.create_webhook(name=ctx.author.name)
        await web.send(embed=e, avatar_url=ctx.author.avatar_url)
        await web.delete()
        await ctx.message.delete()

    @commands.command()
    async def roll(self, ctx, *, dice: str = None):
        result = []
        sum = 0
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception as e:
            print(e)
            try:
                ndice = int(dice)
                embed = discord.Embed(
                    title=f"Rolls- **1d{ndice}**", description=f'You rolled a **{random.randint(1, ndice)}**',
                    color=0x7ae19e)
                await ctx.reply(embed=embed)
                return
            except Exception:
                embed = discord.Embed(
                    title="Error", description='Please only use the **NdN** format', color=0x7ae19e)
                await ctx.reply(embed=embed)
                return

        for r in range(rolls):
            result.append(random.randint(1, limit))

        for r in range(len(result)):
            sum += result[r]

        if rolls == 1:
            embed = discord.Embed(
                title=f"Rolls- **{dice}**", description=f'{result[0]}', color=0x7ae19e)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Rolls- **{dice}**", description=f'{sum} - {result}', color=0x7ae19e)
            await ctx.send(embed=embed)

    @commands.command()
    async def birthday(self, ctx, date: str):
        now = datetime.datetime.now().strftime("%m/%d")
        await ctx.send(now)
        if now == date:
            await ctx.send("Happy Birthday!")
        if len(date.split('/')[0]) == 2 and len(date.split('/')[1]) == 2:
            async with aiosqlite3.connect('idiotbot.db') as db:
                await db.execute("INSERT INTO birthdays (person, date) VALUES (?, ?)", (ctx.author.id, date))
                await db.commit()
            e = discord.Embed(
                title="Success.", description=f"Birthday set to {date}!", color=0x7ae19e)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(
                title="Error you idiot",
                description="You have to use the format `mm/dd`, alright? It's simple, like this one for May 17th: `05/17`. Okay?",
                color=0xdf4e4e)
            await ctx.send(embed=e)

    @commands.command()
    async def monke(self, ctx):
        e = discord.Embed(title='MONKE?????')
        e.set_image(url='https://www.placemonkeys.com/500/350?random')
        await ctx.send(embed=e)

    @commands.command()
    async def eat(self, ctx, *, eat:str='nothing'):
        await ctx.send(f' :point_right: {eat} <:OMEGALUL:803681453715226645> {(ctx.author.name if ctx.author.nick == None else ctx.author.nick)}')

    @commands.command()
    async def praise(self, ctx):
        '''Praise the Sun'''
        await ctx.send('https://i.imgur.com/K8ySn3e.gif')


def setup(client):
    print("Cog 'Fun' Ready.")
    client.add_cog(Fun(client))
