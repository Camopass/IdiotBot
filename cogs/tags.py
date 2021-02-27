import discord, asyncio, sqlite3
from discord.ext import commands
global green, red
green = 0x7ae19e
red = 0xdf4e4e

class tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def tag(self, ctx, *args):
        if len(args) == 0:
            e = discord.Embed(title='Tags', color=green)
            await ctx.reply(embed=e)
        if args[0] in ['add', 'create', 'make']:
            conn = sqlite3.connect('tags.db')
            c = conn.cursor()

            data = c.execute('SELECT * FROM tags WHERE name=?', (args[1],))

            e = 0
            for row in data:
                if row[0] == args[1]:
                    e = discord.Embed(title='Error', description=f'Tag: {args[1]} already in use. Please contact the owner of the tag({str(self.bot.get_user(row[2]))}) or choose another name.', color=red)
                    await ctx.reply(embed=e)
                    e = 1

            if e != 1:
                msg = await ctx.send()
                c.execute('INSERT INTO tags VALUES (?, ?, ?)', (args[1], ' '.join(args[2:]), ctx.author.id))
                conn.commit()
                conn.close()
                await msg.delete()
                e = discord.Embed(title=f'Success. Tag: **{args[1]}** created.', description=' '.join(args[2:]), color=green)
                await ctx.send(embed=e)
        elif len(args) != 0:
            tag = ' '.join(args)

            conn = sqlite3.connect('tags.db')
            c = conn.cursor()

            data = c.execute('SELECT * FROM tags WHERE name=?', (tag,))
            print(data)
            for row in data:
                print(row)


def setup(client):
    client.add_cog(tags(client))
