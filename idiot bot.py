# Stupid idiot bot V1.03
import aiosqlite3
import asyncio
import discord
import fuzzywuzzy
import math
import os
import platform
import random
import traceback
import datetime
import json
import unicodedata
import sys
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands, menus
from fuzzywuzzy import process

import idiotlibrary
from idiotlibrary import trim_str, convert_emoji, red, green

config = json.loads(open(r'E:\workspace\idiotbot\config.json').read())
databasedir = config['Database Directory']
OWNER_ID = config['BotOwnerID']
default_prefix = config['DefaultPrefix']
token_dir = config['token.txt Directory']

with open(token_dir, "r") as myfile:
    token = str(myfile.readlines()[0])


async def getPrefix(bot, message):
    if message.guild is not None:
        db = await aiosqlite3.connect(databasedir)
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        if not row is None:
            await cursor.close()
            await db.close()
            return commands.when_mentioned_or(row[0])(bot, message)
        else:
            await db.execute('INSERT INTO prefixes VALUES (?, ?)', (default_prefix, message.guild.id))
            await db.commit()
            await db.close()
            return commands.when_mentioned_or(default_prefix)(bot, message)
    elif message.guild is None:
        return default_prefix


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=getPrefix, intents=intents, case_insensitive=True)

bot.remove_command('help')
invischaracter = "ㅤ"

jumpUrlUrls = ['https://canary.discord.com/channels/', 'https://discord.com/channels/',
               'https://discordapp.com/channels/']


def get_emotes(message2):
    message1 = message2
    def get_emote(message: str):
        eIndex = message.index(':')
        e = message[eIndex + 1:]
        if ':' in e:
            eIndex = e.index(':')
            e2 = e[:eIndex]
            return e2
    x = get_emote(message1)
    result = [x]
    msg = ':'
    t = 0
    while ':' in msg and t <= 100:
        msg = message1
        for i in result:
            msg = msg.replace(f':{i}:', '')
        if ':' in msg:
            x = get_emote(msg)
            result.append(x)
        t += 1
    return result


async def getGuildPrefix(guild_id):
    db = await aiosqlite3.connect(databasedir)
    cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (guild_id,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row[0]


def get_all_emotes():
    result = []
    for guild in bot.guilds:
        for emote in guild.emojis:
            result.append(emote)

    return result


class embedToMessage:
    def __init__(self, embed_message):
        embed = embed_message.embeds[0]
        self.content = embed.description
        self.author = embed_message.author
        self.guild = embed_message.guild
        self.channel = embed_message.channel
        self.embed = embed


class CustomMessage:
    def __init__(self, content, embed, channel, guild, author):
        self.content = content
        self.embeds = embed
        self.channel = channel
        self.guild = guild
        self.author = author


async def msgReference(message, urltype):
    if urltype in message.content and not message.author.bot:  # This detects if a link is in the message
        url = f"{urltype}{message.content.split(urltype, 2)[1]}"  # Get the URL for the message
        if " " in url:  # ---------------------------
            url = url.split(" ", 2)[0]  # ---------------------------
        # await message.channel.send(url)                                                                                           #  ---------------------------
        context = CustomCtx(message, bot, message.guild, message.channel,
                            message.author)  # Create a context object so we can use MessageConverter()
        nmessage = await discord.ext.commands.MessageConverter().convert(context,
                                                                         url)  # Fetch the message from the link, using the url and the custom context
        e = discord.Embed(title=f"Message referenced by {message.author}", description=nmessage.content,
                          color=0x7ae19e)  # Create the embed object
        e.set_author(name=nmessage.author.name)  # Add the name of the person who sent the message to the embed
        if len(nmessage.attachments) != 0:  # Detect if there is an attachment on the linked message
            if nmessage.attachments[0].height != 0:  # Is the attachment an image?
                e.set_image(url=nmessage.attachments[0].url)
        return e, nmessage
    else:
        return 0, 0


async def get_guild_members(guild):
    e = 0
    async for member in guild.members:
        if not member.bot:
            e += 1
    return e

class CustomCtx:  # Custom context for the jump_url detection
    def __init__(self, message, bot, guild, channel, author):
        self.message = message
        self.bot = bot
        self.guild = guild
        self.channel = channel
        self.author = author


def inMessage(semote, emotes):
    for emote in emotes:
        if semote.name == emote.name:
            return True


words = ["person", "world", "hand", "woman", "place", "point", "government", "company", "number", "problem", "little"]

questions = {
    "What is the full name of Notch?": ["`Markus A. Persson", "Demetrius R. Nossville", "[SWEDISH NAME HERE]",
                                        "Markus A. Noth"],
    "Which game inspired Notch to make Minecraft?": ["`Infiniminer", "Cave Game", "Roblox", "Your mum"]
}

q = list(questions.keys())


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------------')


@bot.event
async def on_command_error(ctx, error):
    if ctx.guild is None and ctx.author.id != OWNER_ID:
        e = discord.Embed(title="You broke me you idiot",
                          description=f"You gave me an error, what are you? British? ```{error}```", color=red)
        await ctx.send(embed=e)
        await bot.get_channel(808831381592866847).send(f"Bot: Stupid Idiot Bot ```{error}```")
    elif (not isinstance(error, commands.CommandNotFound)) and ctx.guild is not None:
        e = discord.Embed(title="You broke me you idiot",
                            description=f"You gave me an error, what are you? British? ```{error}```", color=red)
        await ctx.send(embed=e)
        channel = bot.get_channel(808831381592866847)
        e = discord.Embed(title='Error',
                            description=f'Exception in: **{ctx.command.name}** in channel **{ctx.channel.name}**.',
                            color=red)
        t = (ctx.message.created_at - datetime.timedelta(hours=5)).strftime('%A the %d, %B, %Y at %I:%M %p')
        e.add_field(name=f'Message:', value=f'```{trim_str(ctx.message.content, 1018)}```')
        e.add_field(name='Time sent:', value=f'```Message sent at {t}```')
        e.add_field(
            name='Error:', value=f'```{error}```')
        e.set_footer(text=f'Error in channel: {ctx.channel.name}: {ctx.guild.name}', icon_url=ctx.guild.icon_url)
        e.set_thumbnail(url=ctx.guild.icon_url)
        await channel.send(embed=e)
        if ctx.author.id != OWNER_ID or ctx.guild.id == 559474847176982543:
            raise error
    elif isinstance(error, commands.CommandNotFound):
        message = ctx.message
        db = await aiosqlite3.connect(databasedir)
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        await cursor.close()
        await db.close()
        prefix = row[0]
        command = ctx.message.content.strip(prefix)
        command = command.split(' ')[0] if ' ' in command else command
        commands_ = bot.commands
        best_command = process.extract(command, commands_, limit=1)
        e = discord.Embed(title='Error',
                          description=f'You absolute donut. There is no command called `{command}` There is, however, a command called `{prefix}{best_command[0][0].name}`.',
                          color=red)
        await ctx.send(embed=e)


@bot.event  # This lets you see a message that has been linked
async def on_message(message):
    if message.guild is None:
        return await bot.process_commands(message)
    if not message.guild is None:
        for url in jumpUrlUrls:
            originalMessage, referencedMessage = await msgReference(message, url)
            if originalMessage != 0:
                await referencedMessage.reply(embed=originalMessage, mention_author=False)
            break
        if ':' in message.content and message.content.count(':') >= 2 and not message.author.bot:
            result = message.content
            emotes = get_emotes(message.content)
            availableEmotes = get_all_emotes()
            messageEmotes = []
            for emote in availableEmotes:
                if (emote.name in emotes) and not (inMessage(emote, messageEmotes)):
                    messageEmotes.append(emote)
            for emote in messageEmotes:
                if not inMessage(emote, message.guild.emojis):
                    result = result.replace(f':{emote.name}:', str(emote))
            if not result == message.content:
                web = await message.channel.create_webhook(name=message.author.name)
                await web.send(result, avatar_url=message.author.avatar_url)
                await web.delete()
                await bot.process_commands(message)
                await message.delete()
    if message.content in ['<@!478709969152376832>', '<@!478709969152376832> ', ' <@!478709969152376832>',
                           ' <@!478709969152376832> ']:
        db = await aiosqlite3.connect(databasedir)
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        await cursor.close()
        await db.close()
        prefix = row[0]
        e = discord.Embed(title='Stupid Idiot Bot',
                          description=f'Hello! You can use this bot by using the prefix "{prefix}" You can also just mention the bot.',
                          color=green)
        await message.reply(embed=e)
    if message.content == 'jump_url':
        msg = message.reference
        msg = str(msg.message_id)
        # Create a context object so we can use MessageConverter()
        context = CustomCtx(
            message, bot, message.guild, message.channel, message.author)
        msg = await discord.ext.commands.MessageConverter().convert(context, msg)
        await message.reply(msg.jump_url)

    '''if not message.author.bot and message.guild.id == 810042880873070652:
        for i in ["im", "i'm", "Im", "I'm", "I am", "i am"]:
            if i in message.content:
                e = message.content.split(i, 2)
                if (e[0] == "" or e[0] == " ") and (e[1][0] == " " or e[1][0] == ""):
                    await message.channel.send(f"Hello **{e[1]}**, I am Dad!")
                    await message.author.edit(nick=e[1])
                    break
                else:
                    if e[0].endswith(" ") and (e[1][0] == " " or e[1][0] == ""):
                        await message.channel.send(f"Hello **{e[1]}**, I am Dad!")
                        await message.author.edit(nick=e[1])
                        break
                    else:
                        break'''

    return await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is None:
        return
    if str(payload.emoji) == '\U0000274c' and payload.user_id == OWNER_ID and payload.channel_id == 813451902774673468:
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.delete()
    async with aiosqlite3.connect(databasedir) as db:
        data = await db.execute('SELECT role_id FROM ReactionRoles WHERE message_id=?', (payload.message_id,))
        for row in data:
            role = bot.get_guild(payload.guild_id).get_role(row[0])
            await payload.member.add_roles(role)
            await payload.member.send('Role added!')


'''@client.event
async def on_raw_reaction_remove(payload):
    if str(payload.emoji) == '\U0000274c':
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        for reaction in message.reactions:
            if str(reaction) == '\U00002705':
                db = await aiosqlite3.connect(databasedir)
                cursor = await db.execute('SELECT channel_id FROM starboard WHERE author_id=?', (payload.guild_id,))
                data = await cursor.fetchone()
                channel = client.get_channel(data[0])
                async for star in channel.history(limit=20):
                    if star.content == payload.message_id:
                        for r in star.reactions:
                            if str(r) == '\U0000274c':
                                scount0 = r.count
                        for r in message.reactions:
                            if str(r) == '\U0000274c':
                                scount1 = r.count
                        e = star.embeds[0]
                        author = e.author.split(' - ')[0]
                        e.set_author(f'{author} - {scount0 + scount1}/{await get_guild_members(message.guild)}')
                        await star.edit(embed=e)
                        return'''


async def to_string(c):
    digit = f'{ord(c):x}'
    return f'\\U{digit:>08}'


@bot.command()
async def charinfo(ctx, *, characters: str):
    """Shows you information about a number of characters.
    Only up to 25 characters at a time.
    """

    def to_string(c):
        digit = f'{ord(c):x}'
        name = unicodedata.name(c, 'Name not found.')
        return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
    msg = '\n'.join(map(to_string, characters))
    if len(msg) > 2000:
        return await ctx.send('Output too long to display.')
    await ctx.send(msg)


@bot.command(hidden=True)
async def quiz(ctx):
    timelimit = 5.0
    question = random.choice(q)
    answers = list(random.sample(questions[question], len(questions[question])))
    for i in answers:
        if i.startswith('`'):
            pre = answers.index(i)
            x = i
            correct = i.split('`', 1)
            break
    answers.remove(x)
    answers.insert(pre, correct[1])
    # print(question, answers)
    e = discord.Embed(title=question, description=f"Find the correct answer in `{timelimit}` seconds!", colour=0x7ae6d9)
    for i in range(len(answers)):
        e.add_field(name=i + 1, value=answers[i])
    message = await ctx.send(embed=e)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    await message.add_reaction("4️⃣")

    def check(reaction_, user):
        return user == ctx.author

    try:
        reaction = await bot.wait_for('reaction_add', timeout=timelimit, check=check)
    except asyncio.TimeoutError as e:
        await message.edit(
            embed=discord.Embed(title=f"Time out!", description=f"The answer was: `{correct[1]}`", colour=0xe67a7a))
        await asyncio.sleep(10)
        await message.delete()
        await ctx.message.delete()
    else:
        if reaction.emoji == "1️⃣":
            useranswer = 1
        if reaction.emoji == "2️⃣":
            useranswer = 2
        if reaction.emoji == "3️⃣":
            useranswer = 3
        if reaction.emoji == "4️⃣":
            useranswer = 4
        if pre + 1 == useranswer:
            await message.edit(
                embed=discord.Embed(title="Correct!", description=f"The answer was: `{correct[1]}`.", colour=0x7ae687))
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
        else:
            await message.edit(
                embed=discord.Embed(title="Wrong!", description=f"The answer was: `{correct[1]}`.", colour=0xe67a7a))
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()


@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def _reload(ctx, cog="all"):
    async with ctx.typing():
        if cog == "all":
            e = discord.Embed(title=f"Reloading {cog}...", description=f"Reloading Cog: {cog}")
            msg = await ctx.send(embed=e)
            for filename in os.listdir('cogs'):
                if filename.endswith('.py'):
                    bot.unload_extension(f'cogs.{filename[:-3]}')
            await msg.edit(embed=discord.Embed(title=f"Unloaded {cog}...", description=f"Unloaded Cog: {cog}"))
            for filename in os.listdir('cogs'):
                if filename.endswith('.py'):
                    bot.load_extension(f'cogs.{filename[:-3]}')
            await msg.edit(embed=discord.Embed(title=f"Loaded {cog}...", description=f"Loaded Cog: {cog}"))
        else:
            try:
                bot.unload_extension(f"cogs.{cog}")
                msg = await ctx.send(f"Cog: {cog} unloaded.")
                bot.load_extension(f"cogs.{cog}")
                await msg.edit(content=f"Cog: {cog} reloaded successfuly.")
            except commands.ExtensionNotFound:
                await ctx.send("Could not find Cog: {cog}.")

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f'Loaded {filename}')

bot.load_extension('jishaku')

bot.run(token)
