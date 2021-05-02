import discord
import os
import aiosqlite3
from discord.ext import commands
from discord.ext import menus
from fuzzywuzzy import process

import idiotlibrary

from idiotlibrary import red, green


class TagListMenu(menus.Menu):

    async def send_initial_message(self, ctx, channel):
        async with aiosqlite3.connect('tags.db') as db:
            c = await db.execute('SELECT name FROM tags WHERE guild_id=?', (ctx.guild.id,))
            data = c.fetchall()
        e = 0
        self.pagenum = 0
        self.page = commands.Paginator(
            prefix=f'Tags for **{ctx.guild.name}** ```', suffix=f'```', max_size=100)
        for row in data:
            self.page.add_line(line=row[0])
            e += 1
        if e == 0:
            await ctx.send('No tags found.')
            return
        self.page = self.page
        return await ctx.send(embed=discord.Embed(title='Tag List', description=self.page.pages[
                                                  self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page.pages)}',
                                                  color=green))


    @menus.button('\U000023ea')
    async def on_first(self, payload):
        self.pagenum = 0
        await self.message.edit(embed=discord.Embed(title='Tag List', description=self.page.pages[
                                                    self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page.pages)}',
                                                    color=green))


    @menus.button('\U00002b05')
    async def on_left(self, payload):
        self.pagenum = self.pagenum - (1 if not self.pagenum == 0 else 0)
        await self.message.edit(embed=discord.Embed(title='Tag List', description=self.page.pages[
                                                    self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page.pages)}',
                                                    color=green))


    @menus.button('\U000027a1')
    async def on_right(self, payload):
        self.pagenum = self.pagenum + (1 if (self.pagenum + 1) != len(self.page.pages) else 0)
        await self.message.edit(embed=discord.Embed(title='Tag List', description=self.page.pages[
                                                    self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page.pages)}',
                                                    color=green))


    @menus.button('\U000023e9')
    async def on_last(self, payload):
        self.pagenum = len(self.page.pages) - 1
        await self.message.edit(embed=discord.Embed(title='Tag List', description=self.page.pages[
                                                    self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page.pages)}',
                                                    color=green))


    @menus.button('\U000023f9')
    async def on_stop(self, payload):
        await self.message.clear_reactions()
        self.stop()


class tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, tag=None):
        async with aiosqlite3.connect('tags.db') as db:
            c = await db.execute('SELECT * FROM tags WHERE name=? AND guild_id=?', (tag, ctx.guild.id))
            data = await c.fetchone()
        if data is None:
            await ctx.send(f'No tag named **{tag}**.')
        else:
            await ctx.send(data[1])

    
    @tag.command(name='add', ailiases=['make', 'create'])
    async def tag_add(self, ctx, name, *, content):
        async with aiosqlite3.connect('tags.db') as db:
            data = await db.execute(
                'SELECT * FROM tags WHERE name=? AND guild_id=?', (name, ctx.guild.id))
            e = 0
            for row in data:
                if row[0] == name:
                    e = discord.Embed(title='Error',
                                      description=f'Tag: {name} already in use. Please contact the owner of the tag({str(self.bot.get_user(row[2]))}) or choose another name.',
                                      color=red)
                    await ctx.reply(embed=e)
                    e = 1
            if e != 1:
                msg = await ctx.send('Creating Tag...')
                await db.execute('INSERT INTO tags VALUES (?, ?, ?, ?)',
                          (name, content, ctx.author.id, ctx.guild.id))
                await db.commit()
            await msg.delete()
            e = discord.Embed(title=f'Success. Tag: **{name}** created.', description=content,
                                color=green)
            await ctx.send(embed=e)


    @tag.command(name='search')
    async def tag_search(self, ctx, query:str):
           if query == '':
                return await ctx.send('Query cannot be None. Please enter a search value.')
           async with aiosqlite3.connect('tags.db') as db:
                cursor = await db.execute('SELECT name FROM tags WHERE guild_id=?', (ctx.guild.id,))
                data = await cursor.fetchall()
           tagnames = []
           for row in data:
               tagnames.append(row[0])
           tagnames = process.extract(query, tagnames, limit=5)
           sorted_ = []
           for item in tagnames:
               sorted_.append(item[0])
           sorted_ = '\n'.join(sorted_)
           embed = discord.Embed(title=f'Tags matching query: **{query}**', description=f'```\n{sorted_}```',
                               color=green)
           await ctx.send(embed=embed)
    

    @tag.command(name='list')
    async def tag_list(self, ctx):
        list_ = TagListMenu()
        await list_.start(ctx)
    

    @tag.command(name='edit')
    async def tag_edit(self, ctx, name:str, *, value:str):
        async with aiosqlite3.connect('tags.db') as db:
            c = await db.execute('SELECT * FROM tags WHERE guild_id=? AND name=?',
                        (ctx.guild.id, name))
            data = tuple(await c.fetchone())
            if not data is None and ctx.author.id == data[2]:
                c.execute('UPDATE tags SET value = ? WHERE name=? AND guild_id=?',
                            (value, name, ctx.guild.id))
                await db.commit()
                e = discord.Embed(
                    title='Success', description=f'Tag: **{name}** updated.', color=green)
                await ctx.send(embed=e)
            elif data is None:
                e = discord.Embed(
                    title='Error', description='This tag doesn\'t exist, idiot.', color=red)
            else:
                e = discord.Embed(title='Error',
                                    description='You do not own this tag. Please contact the owner of this tag to ask them to edit it or delete it.',
                                    color=red)
                await ctx.send(embed=e)
    

    @tag.command(name='delete', aliases=['remove', 'kill'])
    async def tag_delete(self, ctx, *, tag:str):
        async with aiosqlite3.connect('tags.db') as db:
            c = await db.execute(
                'SELECT * FROM tags WHERE name=? AND guild_id = ?', (tag, ctx.guild.id))
            data = c.fetchone()
            try:
                if ctx.author.id == data[2]:
                    c.execute(
                        'DELETE FROM tags WHERE name=? AND guild_id=?', (tag, ctx.guild.id))
                    await db.commit()
                    await ctx.send(f'Successfully deleted tag **{tag}**')
                else:
                    e = discord.Embed(
                        title='Error', description='You do not own this tag.', color=red)
                    await ctx.send(embed=e)
            except TypeError:
                await ctx.send('Could not find that tag.')
    

    @tag.command(name='info')
    async def tag_info(self, ctx, *, name:str):
        async with aiosqlite3.connect('tags.db') as db:
            c = await db.execute('SELECT * FROM tags WHERE guild_id=? AND name=?',
                      (ctx.guild.id, name))
            data = c.fetchone()
            e = discord.Embed(title=data[0],
                              description=f'**Name:** {data[0]} \n **Author**: {self.bot.get_user(data[2]).mention}',
                              color=green)
            await ctx.send(embed=e)
    

    @tag.error
    async def tag_error(self, ctx, error):
        raise error


def setup(client):
    client.add_cog(tags(client))


if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:/workspace/idiotbot/idiot bot.py"')