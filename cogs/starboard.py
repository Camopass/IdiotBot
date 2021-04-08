import discord
from discord.ext import commands

import aiosqlite3
import aiohttp
import time
import datetime
import math
import asyncio
import os

import idiotlibrary

from idiotlibrary import get_non_bot_members, convert_emoji, to_string, name, get_raw_count, red, green
# -----

'''

Starboard will be customizable with the emoji, limit, and the channel.
It will be fully asynchronous.
If you have an image link, it will find the image link and attach it to the embed as an image.
You can react to either the starred message or the starboard message, but not both.
It will have the date and time of the original star

TODO

-- Add image grabbing
-- Fix custom emojis

'''

# -----

#Variables

star_emoji = '\U00002b50'
star_color = 0xf2d202

#I do not want it to allow any files that could run.
accepted_filetypes = [
    'png',
    'jpg',
    'jpeg',
    'webp',
    'mp4',
    'mp3',
    'txt',
    'bmp',
    'jfif'
]

async def get_star_count(message0, message1, emoji_name):
    reaction_count_1 = []
    for reaction in message0.reactions:
        if str(reaction.emoji) == emoji_name:
            async for user in reaction.users():
                reaction_count_1.append(user)
    for reaction in message1.reactions:
        if str(reaction) == emoji_name:
            async for user in reaction.users():
                if not user in reaction_count_1:
                    reaction_count_1.append(user)
    return len(reaction_count_1) - 1
#Exceptions

class NoStarboardFound(Exception):
    #No starboard was found in database
    pass

class MessageNotSent(Exception):
    #Message has not been sent yet
    pass

#Classes


class CustomCtx:  # Custom context for the jump_url detection
    def __init__(self, message, bot):
        self.message = message
        self.bot = bot
        self.guild = message.guild
        self.channel = message.channel
        self.author = message.author


async def StarboardMessage(message, star_count, starboard_id=None):
    star = StarboardMessage_()
    return await star.init(message, star_count, starboard_id)

class StarboardMessage_:
    @classmethod
    async def init(self, message, star_count, starboard_id=None):
        #Static class construction
        self.original_message = message
        self.author = message.author
        self.icon_url = message.author.avatar_url
        self.jump_url = message.jump_url
        self.guild_id = message.guild.id
        self.count = star_count
        self.starboard_id = starboard_id
        self.channel = message.channel
        #Variable construction
        db = await aiosqlite3.connect('idiotbot.db')
        async with db.execute('SELECT * FROM starboards WHERE guild_id=?', (self.guild_id,)) as cursor:
            for row in cursor:
                is_starboard = True
                #Store that there is starboard data there
                self.starboard_id = row[0]
                self.emoji_name = row[1]
                self.limit = row[2]
        if not is_starboard:
            raise NoStarboardFound(
                'No starboard was found when creating a message.')
        await db.close()
        self.embed = discord.Embed(title='Message', url=self.jump_url, description=self.original_message.content,
                                   color=star_color)
        self.embed.add_field(name='Jump!', value=f'[Jump!]({self.jump_url})')
        author = name(self.author).replace('-', '_')
        self.embed.set_author(
            name=f'{author} - {star_count}', icon_url=self.icon_url)
        #Set up the message embed
        self.attachments = []
        attachments = self.original_message.attachments
        for attachment in attachments:  # Attach any images from the original message to the starboard message
            if attachment.filename.split('.')[1] in accepted_filetypes:
                if attachments.index(attachment) == 0 and not attachment.width == 0:
                    self.embed.set_image(url=attachment.url)
                else:
                    self.attachments.append(attachment)
        # Later I will add image extraction from urls for the bot.
        # There will also be embed starring
        return self
    
    async def send(self, bot, guild_id):
        if self.starboard_id != None:
            self.message = await bot.get_channel(self.starboard_id).send(embed=self.embed)
            await self.message.add_reaction(self.emoji_name.strip('<>'))
        else:
            db = await aiosqlite3.connect('idiotbot.db')
            async with db.execute('SELECT channel_id FROM starboards WHERE guild_id=?', (guild_id,)) as cursor:
                is_starboard = False
                for row in cursor:
                    is_starboard = True
                    channel = bot.get_channel(row[0])
                if not is_starboard:
                    raise NoStarboardFound('No starboard was found while sending a starboard message.')
                else:
                    message = await channel.send(content=self.original_message.id, embed=self.embed)
                    self.message = message
                    await self.message.add_reaction(self.emoji_name.strip('<>'))
                    return message

    async def remove(self):
        try:
            return await self.message.delete()
        except Exception:
            raise MessageNotSent('Cannot remove message that has not been sent.')

    async def update(self):
        try:
            await self.message.edit(content=self.original_message.id, embed=self.embed)
            return self.message
        except Exception:
            raise MessageNotSent('Cannot edit message that has not been sent.')

    async def edit_star_count(self, star_count):
        self.count = star_count
        author = f'{name(self.author)} - {star_count}'
        self.embed.set_author(name=author, icon_url=self.icon_url)
        #pylint:disable=too-many-function-args
        await self.update(self)
        return self.message

async def StarboardFromMessage(message_, limit, bot):
    try:
        embed = message_.embeds[0]
    except IndexError:
        raise RuntimeError('This is not a starboard message')
    url = embed.fields[0].value # [Jump!](URL)
    url = url.split('(')[1] # URL)
    url = url.split(')')[0] # URL
    ctx = CustomCtx(message_, bot)
    message = await commands.MessageConverter().convert(ctx, url)
    message = await StarboardMessage(message, limit)
    message.message = message_
    return message

#Main

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id == None:
            return
        if payload.member.bot:
            return
        count = await get_raw_count(self.bot, payload)
        db = await aiosqlite3.connect('idiotbot.db') #Connect to database
        async with db.execute('SELECT emoji_name, limit_, channel_id FROM starboards WHERE guild_id=?', (payload.guild_id,)) as cursor: #Get the emoji name and the star limit
            is_starboard = False
            for row in cursor:
                is_starboard = True #Make sure that there is a starboard
                emoji = row[0]
                limit = row[1]
                channel_id = row[2]
                if payload.channel_id == channel_id:
                    message0 = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    message = await StarboardFromMessage(message0, limit, self.bot)
                    await message.edit_star_count(message, await get_star_count(message.original_message, message0, emoji))
                    return
        await db.close()
        if not is_starboard:
            return #Do not do anything if there is no starboard in this server
        else:
            if str(payload.emoji) == emoji and count >= limit:
                message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                for reaction in message.reactions:
                    if str(reaction.emoji) == idiotlibrary.check_mark_emoji:
                        async for user in reaction.users():
                            if user == self.bot.user:
                                star_channel = self.bot.get_channel(channel_id)
                                async for star in star_channel.history(limit=200):
                                    if len(star.embeds) == 1 and star.author == self.bot.user and star.content.startswith(str(payload.message_id)):
                                        star = await StarboardFromMessage(star, limit, self.bot)
                                        star_count = await get_star_count(star.message, message, emoji)
                                        await star.edit_star_count(star, star_count)
                                        break
                                return
                star_message = await StarboardMessage(message, limit)
                await star_message.send(star_message, self.bot, payload.guild_id)
                await message.add_reaction(idiotlibrary.check_mark_emoji)

    @commands.group(description='Allows users to add the :star: reaction (or a custom one) to add a message to a new channel called \"starboard\"')
    async def starboard(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Starboard Help",
                              description="Allows users to add the :star: reaction (or a custom one) to add a message to a new channel called \"starboard\"",
                              colour=0xdf4e4e)
            await ctx.reply(embed=e)

    @starboard.command(name='add', description='Use {0}starboard add <emoji> <limit> to set starboard to the channel that the message is in. By default, emoji will be :star: and the limit will be 10 or the amount of members in the server divided by two and rounded up.')
    @commands.has_permissions(administrator=True)
    async def starboard_add(self, ctx, emoji:idiotlibrary.StarboardEmojiConverter=star_emoji, limit:int=None):
        if limit is None:
            members = await get_non_bot_members(ctx.guild)
            limit = 10 if members > 20 else math.ceil(members / 2)
        msg = await ctx.send(embed=discord.Embed(title='Confirm',
         description=f'Are you sure that you want to add a starboard to **{ctx.guild.name}**, channel **{ctx.channel.name}**, with the emoji {emoji} and the limit {limit}?',
         color=green))
        await msg.add_reaction(idiotlibrary.check_mark_emoji)
        await msg.add_reaction(idiotlibrary.red_x_emoji)
        def check(reaction, user):
            return user == ctx.author
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('No response found. Cancelling staboard.', delete_after=10)
        else:
            if str(reaction) == idiotlibrary.red_x_emoji:
                await msg.edit(embed=discord.Embed(title='Starboard Cancelled', description='Starboard has been cancelled. You can use `starboard add <emoji> <limit>` to add a new one. These will be determined automatically if left out.', colour=red))
                await msg.clear_reactions()
                return
            elif str(reaction) == idiotlibrary.check_mark_emoji:
                await msg.edit(embed=discord.Embed(title='Okay!', description='Adding Starboard to your server...', colour=green))
                async with aiosqlite3.connect('idiotbot.db') as db:
                    await db.execute('INSERT INTO starboards VALUES (?, ?, ?, ?)', (ctx.channel.id, emoji, limit, ctx.guild.id))
                    await db.commit()
                await msg.edit(embed=discord.Embed(title='Starboard Added!', description=f'A starboard has been added to: ```\nserver: {ctx.guild.name},\nchannel: {ctx.channel.name},\nemoji: {emoji},\nlimit: {limit}```', colour=green))

    @starboard.command(name='remove', description='Remove the starboard from your server.')
    @commands.has_permissions(administrator=True)
    async def starboard_remove(self, ctx):
        embed = discord.Embed(title='Confirm',
        description=f'Are you sure you want to remove starboard from **{ctx.guild.name}**?', color=green)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(idiotlibrary.check_mark_emoji)
        await msg.add_reaction(idiotlibrary.red_x_emoji)
        def check(reaction, user):
            return user == ctx.author
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('No response. Cancelling starboard remove.', delete_after=10.0)
            await msg.delete()
        else:
            if str(reaction) == idiotlibrary.red_x_emoji:
                await msg.edit(embed=discord.Embed(title='Cancelled', description='Starboard remove has been cancelled. You can use `starboard remove` to remove it at any time.', color=red))
                return
            elif str(reaction) == idiotlibrary.check_mark_emoji:
                async with aiosqlite3.connect('idiotbot.db') as db:
                    await db.execute('DELETE FROM starboards WHERE guild_id=?', (ctx.guild.id,))
                    await db.commit()
                await msg.edit(embed=discord.Embed(title='Removed Starboard', description=f'Removed starboard from guild **{ctx.guild.name}**.', color=green))



def setup(bot):
    bot.add_cog(Starboard(bot))

if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:\workspace\idiotbot\idiot bot.py"')
