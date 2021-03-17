import discord
from discord.ext import commands

import aiosqlite3
import aiohttp
import time
import datetime

'''

Starboard will be customizable with the emoji, limit, and the channel.
It will be fully asynchronous.
If you have an image link, it will find the image link and attach it to the embed as an image.
You can react to either the starred message or the starboard message, but not both.
It will have the date and time of the original star

'''

star_emoji = '\U00002b50'
star_color = 0xf2d202

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

async def get_non_bot_members(guild):
    members = 0
    for member in guild.members:
        if not member.bot:
            members += 1
    return members

async def name(user):
    if user.nick == None:
        return user.name
    else:
        return user.nick

async def to_string(c):
    digit = f'{ord(c):x}'
    return fr'\{digit:>08}'

async def convert_emoji(ctx, emoji):
    try:
        emoji = await commands.EmojiConverter().convert(ctx, emoji)
    except commands.BadArgument:
        emoji = await to_string(emoji)
    finally:
        return emoji


class NoStarboardFound(Exception):
    pass

class MessageNotSent(Exception):
    pass


class StarboardMessage:
    async def __init__(self, message, star_count, starboard_id = None):
        #Basic class construction
        self.original_message = message
        self.author = message.author
        self.icon_url = message.author.icon_url
        self.jump_url = message.jump_url
        self.guild_id = message.guild.id
        self.count = star_count
        self.starboard_id = starboard_id
        #More advanced construction
        db = await aiosqlite3.connect('idiotbot.db')
        async with db.execute('SELECT * FROM starboards WHERE guild_id=?', (self.guild_id)) as cursor:
            async for row in cursor:
                is_starboard = True
                #Store that there is starboard data there
                self.emoji_name = row[1]
                self.limit = row[2]
                self.starboard_id = row[0]
        if not is_starboard:
            #If there is not a starboard, add one to the starboards database. Deciding wether or not to do so will be decided when calling.
            mem_count = await get_non_bot_members(self.original_message.guild.id)
            await db.execute('INSERT INTO starboards VALUES (?, ?, ?, ?)', (self.original_message.channel.id,
             star_emoji, mem_count / 2 if mem_count < 20 else 10), self.guild_id)
            await db.commit()
        await db.close()
        self.embed = discord.Embed(title='Message', url=self.jump_url, description=self.original_message.content,
        color=star_color)
        self.embed.add_field(name='Jump!', value=self.jump_url)
        author = await name(self.author).replace('-', '_')
        self.embed.set_author(name=f'{author} - {star_count}', icon_url=self.icon_url)
        #Set up the message embed
        self.attachments = []
        attachments = self.original_message.attachments
        async for attachment in attachments: #Attach any images from the original message to the starboard message
            if attachment.filename.split('.')[1] in accepted_filetypes:
                if attachments.index(attachment) == 0:
                    self.embed.set_image(url=attachment.url)
                else:
                    self.attachments.append(attachment)
        # Later I will add image extraction from urls for the bot.
    
    async def send(self, bot, guild_id):
        if self.starboard_id != None:
            await bot.get_channel(self.starboard_id).send(self.embed)
        else:
            db = await aiosqlite3.connect('idiotbot.db')
            async with db.execute('SELECT channel_id FROM starboards WHERE guild_id=?', (guild_id,)) as cursor:
                async for row in cursor:
                    is_starboard = True
                    channel = await bot.get_channel(row[0])
                if not is_starboard:
                    raise NoStarboardFound('No starboard was found while sending a starboard message.')
                else:
                    message = await channel.send(content=self.original_message.id, embed=self.embed)
                    self.message = message

    async def remove(self):
        try:
            await self.message.delete()
        except:
            raise MessageNotSent('Cannot remove message that has not been sent.')

    async def update(self):
        try:
            await self.message.edit(embed=self.embed)
        except:
            raise MessageNotSent('Cannot edit message that has not been sent.')

    async def edit_star_count(self, star_count):
        author = self.embed.author
        author = author.split(' - ')[1]



class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        db = await aiosqlite3.connect('idiotbot.db')
        async with db.execute('SELECT emoji_name, limit_ FROM starboards WHERE guild_id=?', (payload.guild_id,)) as cursor:
            is_starboard = False
            for row in cursor:
                is_starboard = True
                emoji = row[0]
                limit = row[1]
            if not is_starboard:
                return
            else:
                if str(payload.emoji) == emoji:
                    message = self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    star_message = await StarboardMessage(message, limit)
                    await star_message.send(self.bot, payload.guild_id)

    @commands.group()
    async def starboard(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Starboard Help",
                              description="Allows users to add the :star: reaction (or a custom one) to add a message to a new channel called \"starboard\"",
                              colour=0xdf4e4e)
            await ctx.reply(embed=e)

    @starboard.command(name='add')
    @commands.has_permissions(administrator=True)
    async def starboard_add(self, ctx, emoji=None, limit=None):
        if limit == None:
            members = await get_non_bot_members(ctx.guild)
            if members < 20:
                limit = members / 2
            else:
                limit = 10
        channel = ctx.channel
        await ctx.send(f"Starboard channel now set to {channel.mention}")
        async with aiosqlite3.connect('idiotbot.db') as db:
            async with db.execute('SELECT channel_id, emoji_name FROM starboards WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                e = 0
                for row in cursor:
                    e += 1
                    if emoji == None:
                        emoji = row[1]
                    else:
                        emoji = await convert_emoji(ctx, emoji)
                        await ctx.send(f'`{emoji}`')
                if e == 0:
                    await db.execute('INSERT INTO starboards VALUES (?, ?, ?, ?)', (ctx.channel.id, emoji, limit, ctx.guild.id))
                    await db.commit()
                elif e == 1:
                    await db.execute('UPDATE starboards SET channel_id = ? WHERE guild_id = ?',
                                     (channel.id, ctx.guild.id))
                    await db.commit()
                else:
                    await ctx.send(
                        'How did you get multiple starboard channels? Oh well, better fix that I guess. <:LULW:771564349185327154>')
                    await db.execute('DELETE FROM starboard WHERE guild_id = ?', (ctx.guild.id,))
                    await db.execute('INSERT INTO starboards VALUES (?, ?, ?, ?)', (ctx.channel.id, emoji, limit, ctx.guild.id))
                    await db.commit()
        await ctx.send(f"Success. All Starboard Notifications will be sent here. Limit will be {limit} and emoji will be {chr(emoji)}")

    @starboard.command(name='remove')
    @commands.has_permissions(administrator=True)
    async def starboard_remove(self, ctx):
        await ctx.send(f"Removing Starboard from channel {ctx.channel.mention}")
        async with aiosqlite3.connect('idiotbot.db') as db:
            await db.execute('DELETE FROM starboard WHERE guild_id = ?', (ctx.guild.id,))




def setup(bot):
    bot.add_cog(Starboard(bot))
