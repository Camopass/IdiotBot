import discord, asyncio, random, datetime, time, sqlite3
from discord.ext import commands
global green, red
green = 0x7ae19e
red = 0xdf4e4e

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def jesuslaser(self, ctx, *, target: str):
        msg = await ctx.send("Targeting.")
        await asyncio.sleep(1)
        await msg.edit(content="Targeting..")
        await asyncio.sleep(1)
        await msg.edit(content="Targeting...")
        await asyncio.sleep(1)
        await msg.edit(content=f"Target: **{target}** found. Deploying Jesus laser.")
        await asyncio.sleep(1)
        await ctx.send("https://media.discordapp.net/attachments/715437307288879154/806980050246697020/images.png?width=231&height=176")

    @commands.command()
    async def embed(self, ctx, title="Title", *, description="Description"):
        e = discord.Embed(description=description, title=title,
                        color=0x7ae19e, author=ctx.author.name)
        e.set_author(name=str(ctx.author.name),
                    icon_url=str(ctx.author.avatar_url))
        if len(ctx.message.attachments) >> 0:
            embed = ctx.message.attachments[0]
            e.set_image(url=embed.url)
        await ctx.send(embed=e)
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
                    title=f"Rolls- **1d{ndice}**", description=f'You rolled a **{random.randint(1, ndice)}**', color=0x7ae19e)
                await ctx.send(embed=embed)
                return
            except Exception:
                embed = discord.Embed(
                    title="Error", description='Please only use the **NdN** format', color=0x7ae19e)
                await ctx.send(embed=embed)
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
    async def birthday(self, ctx, date:str):
        conn = sqlite3.connect('idiotbot.db')
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%m/%d")
        if now == date:
            await ctx.send("Happy Birthday!")
        if len(date.split('/')[0]) == 2 and len(date.split('/')[1]) == 2:
            c.execute("INSERT INTO birthdays (person, date) VALUES (?, ?)", (ctx.author.id, date))
            e = discord.Embed(
                title="Success.", description=f"Birthday set to {date}!", color=0x7ae19e)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(
                title="Error you idiot", description="You have to use the format `mm/dd`, alright? It's simple, like this one for May 17th: `05/17`. Okay?", color=0xdf4e4e)
            await ctx.send(embed=e)
    
def setup(client):
    print("Cog 'Fun' Ready.")
    client.add_cog(Fun(client))
