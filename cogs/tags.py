import discord, asyncio, sqlite3
from discord.ext import commands
from fuzzywuzzy import process
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

            data = c.execute('SELECT * FROM tags WHERE name=? AND guild_id=?', (args[1], ctx.guild.id))

            e = 0
            for row in data:
                if row[0] == args[1]:
                    e = discord.Embed(title='Error', description=f'Tag: {args[1]} already in use. Please contact the owner of the tag({str(self.bot.get_user(row[2]))}) or choose another name.', color=red)
                    await ctx.reply(embed=e)
                    e = 1

            if e != 1:
                msg = await ctx.send('Creating Tag...')
                c.execute('INSERT INTO tags VALUES (?, ?, ?, ?)', (args[1], ' '.join(args[2:]), ctx.author.id, ctx.guild.id))
                conn.commit()
                conn.close()
                await msg.delete()
                e = discord.Embed(title=f'Success. Tag: **{args[1]}** created.', description=' '.join(args[2:]), color=green)
                await ctx.send(embed=e)
        elif args[0].lower() == 'search':
            query = ' '.join(args[1:])
            if query == '':
                return await ctx.send('Query cannot be None. Please enter a search value.')
            conn = sqlite3.connect('tags.db')
            c = conn.cursor()
            c.execute('SELECT name FROM tags WHERE guild_id=?', (ctx.guild.id,))
            data = c.fetchall()
            conn.close()
            tagnames = []
            for row in data:
                tagnames.append(row[0])
            tagnames = process.extract(query, tagnames, limit=5)
            sorted_ = []
            for item in tagnames:
                sorted_.append(item[0])
            sorted_ = '\n'.join(sorted_)
            embed = discord.Embed(title=f'Tags matching query: **{query}**', description= f'```\n{sorted_}```', color=green)
            await ctx.send(embed=embed)
        elif args[0].lower() == 'list':
            pagenum = 0
            page = commands.Paginator(prefix=f'Tags for **{ctx.guild.name}** ```', suffix=f'```', max_size=500)
            conn = sqlite3.connect('tags.db')
            c = conn.cursor()
            c.execute('SELECT name FROM tags WHERE guild_id=?', (ctx.guild.id,))
            data = c.fetchall()
            conn.close()
            for row in data:
                page.add_line(line=row[0])
            msg = await ctx.send(embed= discord.Embed(title='Tag List', description=page.pages[pagenum], color=green))
        elif args[0].lower() == 'edit':
            name = args[1]
            value = ' '.join(args[2:])
            conn = sqlite3.connect('tags.db')
            c = conn.cursor()
            c.execute('SELECT * FROM tags WHERE guild_id=? AND name=?', (ctx.guild.id, name))
            data = c.fetchone()
            if not data == None and ctx.author.id == data[2]:
                c.execute('UPDATE tags SET value = ? WHERE name=? AND guild_id=?', (value, name, ctx.guild.id))
                conn.commit()
                conn.close()
                e = discord.Embed(title='Success', description=f'Tag: **{name}** updated.', color=green)
                await ctx.send(embed=e)
            elif data == None:
                e = discord.Embed(title='Error', description='This tag doesn\'t exist, idiot.', color=red)
            else:
                e = discord.Embed(title='Error',
                 description='You do not own this tag. Please contact the owner of this tag to ask them to edit it or delete it.',
                  color=red)
                await ctx.send(embed=e)
        elif args[0].lower() in ['delete', 'remove', 'kill']:
            tag = args[1]
            conn = sqlite3.connect('tags.db')
            c = conn.cursor()
            c.execute('SELECT * FROM tags WHERE name=? AND guild_id = ?', (tag, ctx.guild.id))
            data = c.fetchone()
            if ctx.author.id == data[2]:
                c.execute('DELETE FROM tags WHERE name=? AND guild_id=?', (tag, ctx.guild.id))
                conn.commit()
                conn.close()
                await ctx.send(f'Successfully deleted tag **{tag}**')
            else:
                conn.close()
                e = discord.Embed(title='Error', description='You do not own this tag.', color=red)
                await ctx.send(embed=e)
        elif args[0].lower() == 'info':
            name = args[1]
            conn = sqlite3.connect('tags.db')
            c = conn.cursor()
            c.execute('SELECT * FROM tags WHERE guild_id=? AND name=?', (ctx.guild.id, name))
            data = c.fetchone()
            e = discord.Embed(title=data[0], description=f'**Name:** {data[0]} \n **Author**: {self.bot.get_user(data[2]).mention}', color=green)
            await ctx.send(embed=e)

        elif len(args) != 0:
            tag = ' '.join(args)

            conn = sqlite3.connect('tags.db')
            c = conn.cursor()

            data = c.execute('SELECT * FROM tags WHERE name=? AND guild_id=?', (tag, ctx.guild.id))
            data = c.fetchone()
            conn.close()
            if data == None:
                await ctx.send(f'No tag named **{tag}**.')
            else:
                e = discord.Embed(title=data[0], description=data[1], color=green)
                await ctx.send(embed=e)
            


def setup(client):
    client.add_cog(tags(client))
