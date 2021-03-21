import discord
from discord.ext import commands

import aiosqlite3
import aiohttp
import time
import datetime
import math

# -----

'''

Starboard will be customizable with the emoji, limit, and the channel.
It will be fully asynchronous.
If you have an image link, it will find the image link and attach it to the embed as an image.
You can react to either the starred message or the starboard message, but not both.
It will have the date and time of the original star

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

#Functions

async def get_non_bot_members(guild):
    members = 0
    for member in guild.members:
        if not member.bot:
            members += 1
    return members
# This gets the member count of any guild that does not include bot members.

def name(user):
    if user.nick == None:
        return user.name
    else:
        return user.nick
#This is shorter than user.name if user.nick == None else user.nick

async def to_string(c):
    digit = f'{ord(c):x}'
    return fr'\{digit:>08}'
#Get the \U value of a character

async def convert_emoji(ctx, emoji):
    try:
        emoji = await commands.EmojiConverter().convert(ctx, emoji)
    except commands.BadArgument:
        emoji = await to_string(emoji)
    finally:
        return emoji.count
#\U if standard emoji and <:name:id> if custom

async def get_raw_count(bot, payload):
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    for reaction in message.reactions:
        if str(reaction.emoji) == str(payload.emoji):
            return reaction.count
    return 0

#Exceptions

class NoStarboardFound(Exception):
    #No starboard was found in database
    pass

class MessageNotSent(Exception):
    #Message has not been sent yet
    pass

#Classes

class StarboardMessage:
    @classmethod
    async def init(self, message, star_count, starboard_id = None):
        #Static class construction
        self.original_message = message
        self.author = message.author
        self.icon_url = message.author.avatar_url
        self.jump_url = message.jump_url
        self.guild_id = message.guild.id
        self.count = star_count
        self.starboard_id = starboard_id
        #Variable construction
        '''db = await aiosqlite3.connect('idiotbot.db')
        async with db.execute('SELECT * FROM starboards WHERE guild_id=?', (self.guild_id)) as cursor:
            async for row in cursor:
                is_starboard = True
                #Store that there is starboard data there
                self.emoji_name = row[1]
                self.limit = row[2]
                self.starboard_id = row[0]
        if not is_starboard:
            raise NoStarboardFound(
                'No starboard was found when creating a message.')
        await db.close()'''
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
                if attachments.index(attachment) == 0 and not  attachment.width == None:
                    self.embed.set_image(url=attachment.url)
                else:
                    self.attachments.append(attachment)
        # Later I will add image extraction from urls for the bot.
        # There will also be embed starring
        return self
    
    async def send(self, bot, guild_id):
        if self.starboard_id != None:
            await bot.get_channel(self.starboard_id).send(self.embed)
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
                    await self.message.add_reaction(star_emoji)
                    return message

    async def remove(self):
        try:
            return await self.message.delete()
        except:
            raise MessageNotSent('Cannot remove message that has not been sent.')

    async def update(self):
        try:
            await self.message.edit(embed=self.embed)
            return self.message
        except:
            raise MessageNotSent('Cannot edit message that has not been sent.')

    async def edit_star_count(self, star_count):
        self.count = star_count
        author = self.embed.author
        author = author.split(' - ')[1]
        author = f'{await name(self.author)} - {author}'
        await self.embed.set_author(name=author, icon_url=self.icon_url)
        await self.update()
        return self.message


'''class StarboardFromMessage(StarboardMessage):
    async def __init__(self, message):
        embed = message.embeds[0]
        url = embed.fields[0].value # [Jump!](URL)
        url = url.split('(')[1] # URL)
        url = url.split(')')[0] # URL
        await message.channel.send(url)'''

#Main

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        count = await get_raw_count(self.bot, payload)
        db = await aiosqlite3.connect('idiotbot.db') #Connect to database
        async with db.execute('SELECT emoji_name, limit_ FROM starboards WHERE guild_id=?', (payload.guild_id,)) as cursor: #Get the emoji name and the star limit
            is_starboard = False
            for row in cursor:
                is_starboard = True #Make sure that there is a starboard
                emoji = row[0]
                limit = row[1]
            if not is_starboard:
                return #Do not do anything if there is no starboard in this server
            else:
                emoji = star_emoji
                members = self.bot.get_guild(payload.guild_id)
                limit = (math.ceil(await get_non_bot_members(members) / 2)) if await get_non_bot_members(members) < 20 else 10
                if str(payload.emoji) == emoji and count >= limit:
                    message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    star_message = await StarboardMessage().init(message, limit)
                    await star_message.send(star_message, self.bot, payload.guild_id)

    @commands.group()
    async def starboard(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Starboard Help",
                              description="Allows users to add the :star: reaction (or a custom one) to add a message to a new channel called \"starboard\"",
                              colour=0xdf4e4e)
            await ctx.reply(embed=e)

    @starboard.command(name='add')
    @commands.has_permissions(administrator=True)
    async def starboard_add(self, ctx):
        return

    @starboard.command(name='remove')
    @commands.has_permissions(administrator=True)
    async def starboard_remove(self, ctx):
        return




def setup(bot):
    bot.add_cog(Starboard(bot))
