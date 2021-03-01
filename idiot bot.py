#Stupid idiot bot V1.03
import discord, requests, json, math, random, asyncio, os, platform, aiohttp, fuzzywuzzy, aiosqlite3
from discord.ext import commands
from discord.ext import menus
from fuzzywuzzy import process
from discord import Webhook, AsyncWebhookAdapter
from discord_slash import SlashCommand, SlashContext

if str(platform.system()) == 'Windows':
    dir = 'E:\\workspace\\idiotbot\\token.txt'
elif str(platform.system()) == "Linux":
    dir = '/home/camopass/discord_token.txt'
else:
    raise(f"Error: System {platform.system()} not recognized.")
with open(dir, "r") as myfile:
    token = str(myfile.readlines()[0])
    print(f"Using token {token}")

async def getPrefix(bot, message):
    if message.guild != None:
        db = await aiosqlite3.connect('idiotbot.db')
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        if not row == None:
            await cursor.close()
            await db.close()
            return commands.when_mentioned_or(row[0])(bot, message)
        else:
            cursor = await db.execute('INSERT INTO prefixes VALUES ("?", ?)', (message.guild.id,))
            await db.commit()
            return commands.when_mentioned_or("?")
    elif message.guild == None:
        return '?'

intents = discord.Intents.all()
client = commands.Bot(command_prefix=getPrefix, intents=intents, case_insensitive=True)
slash = SlashCommand(client)

client.remove_command('help')
invischaracter = "ㅤ"

global green, red
green = 0x7ae19e
red = 0xdf4e4e

jumpUrlUrls = ['https://canary.discord.com/channels/'  ,  'https://discord.com/channels/'  ,  'https://discordapp.com/channels/']

def get_emotes(message2):
    message1 = message2
    def get_emote(message: str):
        eIndex = message.index(':')
        e = message[eIndex+1:]
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

    return(result)

async def getGuildPrefix(guild_id):
    db = await aiosqlite3.connect('idiotbot.db')
    cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (guild_id,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row[0]

def get_all_emotes():
    result = []
    for guild in client.guilds:
        for emote in guild.emojis:
            result.append(emote)

    return result

class embedToMessage:
    def __init__(self, embedmessage):
        embed = embedmessage.embeds[0]
        self.content = embed.description
        self.author = embedmessage.author
        self.guild = embedmessage.guild
        self.channel = embedmessage.channel
        self.embed = embed

class CustomMessage:
    def __init__(self, content, embed, channel, guild, author):
        self.content = content
        self.embeds = embed
        self.channel = channel
        self.guild = guild
        self.author = author

async def msgReference(message, urltype):
    if urltype in message.content and not message.author.bot:                                                                      #  This detects if a link is in the message
        url = f"{urltype}{message.content.split(urltype, 2)[1]}"                                                                   #  Get the URL for the message
        if " " in url:                                                                                                             #  ---------------------------
            url = url.split(" ", 2)[0]                                                                                             #  ---------------------------
        #await message.channel.send(url)                                                                                           #  ---------------------------
        context = CustomCtx(message, client, message.guild, message.channel, message.author)                                       #  Create a context object so we can use MessageConverter()
        nmessage = await discord.ext.commands.MessageConverter().convert(context, url)                                             #  Fetch the message from the link, using the url and the custom context
        e = discord.Embed(title=f"Message referenced by {message.author}", description=nmessage.content, color=0x7ae19e)           #  Create the embed object
        e.set_author(name=nmessage.author.name)                                                                                    #  Add the name of the person who sent the message to the embed
        if len(nmessage.attachments) != 0:                                                                                         #  Detect if there is an attachment on the linked message
            if nmessage.attachments[0].height != 0:                                                                                #  Is the attachment an image?
                e.set_image(url=nmessage.attachments[0].url)
        return e
    else:
        return 0


class MyMenu(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        return await channel.send(f'Hello {ctx.author}')

    @menus.button('\N{THUMBS UP SIGN}')
    async def on_thumbs_up(self, payload):
        await self.message.edit(content=f'Thanks {self.ctx.author}!')

    @menus.button('\N{THUMBS DOWN SIGN}')
    async def on_thumbs_down(self, payload):
        await self.message.edit(content=f"That's not nice {self.ctx.author}...")

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        self.stop()


class CustomCtx:                                                                                                                   # Custom context for the jump_url detection
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
"What is the full name of Notch?": ["`Markus A. Persson", "Demetrius R. Nossville", "[SWEDISH NAME HERE]", "Markus A. Noth"],
"Which game inspired Notch to make Minecraft?": ["`Infiniminer", "Cave Game", "Roblox", "Your mum"]
}

q = list(questions.keys())

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

'''@client.event
async def on_command_error(ctx, error):
    if (not isinstance(error, commands.CommandNotFound)) and ctx.guild != None:
        if (ctx.author.id != 379307644730474496):
            e = discord.Embed(title="You broke me you idiot",
                            description=f"You gave me an error, what are you? British? ```{error}```", color=red)
            await ctx.send(embed=e)
            await client.get_channel(808831381592866847).send(f"Bot: Stupid Idiot Bot ```{error}```")
    elif isinstance(error, commands.CommandNotFound):
        message = ctx.message
        db = await aiosqlite3.connect('idiotbot.db')
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        await cursor.close()
        await db.close()
        prefix = row[0]
        command = ctx.message.content.strip(prefix)
        command = command.split(' ')[0] if ' ' in command else command
        commands_ = client.commands
        bestcommand = process.extract(command, commands_, limit=1)
        e = discord.Embed(title='Error', description=f'You absolute donut. There is no command called `{command}` There is, however, a command called `{prefix}{bestcommand[0][0].name}. `', color=red)
        await ctx.send(embed=e)
    else:
        print(error)'''

@client.event                                                         # This lets you see a message that has been linked
async def on_message(message):
    if not message.guild == None:
        for url in jumpUrlUrls:
            originalMessage = await msgReference(message, url)
            if originalMessage != 0:
                await message.channel.send(embed=originalMessage)
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
                await client.process_commands(message)
                await message.delete()
    if message.content in ['<@!478709969152376832>', '<@!478709969152376832> ', ' <@!478709969152376832>', ' <@!478709969152376832> ']:
        db = await aiosqlite3.connect('idiotbot.db')
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        await cursor.close()
        await db.close()
        prefix = row[0]
        e = discord.Embed(title='Stupid Idiot Bot', description=f'Hello! You can use this bot by using the prefix "{prefix}" You can also just mention the bot.', color=green)
        await message.reply(embed=e)
    if message.guild.id == 472396329683779597:
        if not message.author.bot:
            furrymessage = message.content.lower().replace('r', 'w').replace('l', 'w') + ' ' + random.choice(['UwU', 'OwO', '*nuzzles*', ':pleading_face:'])
            web = await message.channel.webhooks()
            await message.delete()
            furrymessage = await web[0].send(furrymessage, avatar_url=message.author.avatar_url, username=message.author.name if message.author.nick == None else message.author.nick)
            furrymessage.content = message.content
            return await client.process_commands(furrymessage)
    if message.content == 'jump_url':
        msg = message.reference
        msg = str(msg.message_id)
        # Create a context object so we can use MessageConverter()
        context = CustomCtx(
            message, client, message.guild, message.channel, message.author)
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

    return await client.process_commands(message)

@client.event
async def on_raw_reaction_add(payload):
    user = payload.member
    if str(payload.emoji) == "\U00002b50" and not user.bot:
        #get Reaction count and other information
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reactions = message.reactions
        user = message.author
        for reaction in reactions:
            if str(reaction) == "\U00002b50":
                count = reaction.count
                break
        if count == 1:
            members = 0
            for i in user.guild.members:
                if not i.bot:
                    members+=1
            if (count >= math.ceil(members/2)) or count >> 9:
                db = await aiosqlite3.connect('idiotbot.db')
                cursor = await db.execute('SELECT channel_id FROM starboard WHERE guild_id = ?', (message.guild.id,))
                row = await cursor.fetchone()
                if row == None:
                    return await channel.send(f'Hey, {user.mention}, there is no starboard here. You can use `{await getGuildPrefix(payload.guild_id)}starboard add` in the starboard channel to add one.', delete_after=5.0)
                await cursor.close()
                await db.close()
                channel = client.get_channel(row[0])
                e = discord.Embed(title="Message", description=message.content, colour=0xf2d202, url=message.jump_url)
                e.set_author(name=f"{user.name} - {count}/{members}", icon_url=user.avatar_url)
                if len(message.attachments) != 0:
                    embed = message.attachments[0]
                    e.set_image(url=embed.url)
                starboardmessage = await channel.send(message.jump_url, embed=e)
                await message.add_reaction("\U00002705")
                await starboardmessage.add_reaction('\U00002b50')
        else:
            members = 0
            for i in user.guild.members:
                if not i.bot:
                    members+=1
            e = False
            for i in message.reactions:
                if "\U00002705" in str(i):
                    await message.channel.send(f"{user.mention}, Message: {message.jump_url} Already Starboarded.", delete_after=3)
                    e = True
                    break
            if ((count >= math.ceil(members/2)) or count >> 9) and not e:
                db = await aiosqlite3.connect('idiotbot.db')
                cursor = await db.execute('SELECT channel_id FROM starboard WHERE guild_id = ?', (message.guild.id,))
                row = await cursor.fetchone()
                if row == None:
                    return await channel.send(f'Hey, {user.mention}, there is no starboard here. You can use `{await getGuildPrefix(payload.guild_id)}starboard add` in the starboard channel to add one.', delete_after=5.0)
                await cursor.close()
                await db.close()
                channel = client.get_channel(row[0])
                e = discord.Embed(title="Message", description=message.content, colour=0xf2d202, url=message.jump_url)
                e.set_author(name=f"{message.author.name} - {count}/{members}", icon_url=message.author.avatar_url)
                if len(message.attachments) != 0:
                    embed = message.attachments[0]
                    e.set_image(url=embed.url)
                await channel.send(message.jump_url, embed=e)
                await message.add_reaction("\U00002705")
    if str(payload.emoji) == '\U0000274c' and payload.user_id == 379307644730474496 and payload.channel_id == 813451902774673468:
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.delete()


@client.command()
async def menu_example(ctx):
    m = MyMenu()
    await m.start(ctx)

@client.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx, *, prefix=None):
    prefix = prefix.strip('\'"')
    if prefix == None:
        message = ctx.message
        db = await aiosqlite3.connect('idiotbot.db')
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        await cursor.close()
        await db.close()
        prefix = row[0]
        e = discord.Embed(title='Prefix', description=f'Current Prefix is `{prefix}`', color=green)
        await ctx.send(embed=e)
    else:
        message = ctx.message
        db = await aiosqlite3.connect('idiotbot.db')
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
        row = await cursor.fetchone()
        p = row[0]
        if p == prefix:
            await ctx.send('That\'s already the prefix moron.')
        else:
            cursor = await db.execute('UPDATE prefixes SET prefix = ? WHERE author_id = ?', (prefix, ctx.guild.id))
            await db.commit()
            await ctx.send('Prefix updated.')
        await cursor.close()
        await db.close()

@prefix.error
async def prefix_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        e = discord.Embed(title='Error', description='Sorry, only a moderator can change the prefix of the bot.', color=red)
        await ctx.send(embed=e)
        
@client.command()
async def idiot(ctx):
    await ctx.send("I'm an idiot, you moron.")

@slash.slash(name="test")
async def _test(ctx: SlashContext):
    embed = discord.Embed(title="embed test")
    await ctx.send(content="test", embeds=[embed])

@client.command()
async def suggest(ctx, *, suggestion):
    channel = client.get_channel(813451902774673468)
    e = discord.Embed(title=f'Suggestion by *{ctx.author.name}*', description=suggestion, color=green)
    await ctx.send(embed=e)
    msg = await channel.send(embed=e)
    await msg.add_reaction('\U00002705')
    await msg.add_reaction('\U0000274c')

@client.command()
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
    answers.remove(x); answers.insert(pre, correct[1])
    #print(question, answers)
    e = discord.Embed(title=question, description=f"Find the correct answer in `{timelimit}` seconds!", colour=0x7ae6d9)
    for i in range(len(answers)):
        e.add_field(name=i+1, value=answers[i])
    message = await ctx.send(embed=e)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    await message.add_reaction("4️⃣")
    def check(reaction, user):
        return user == ctx.author
    try:
        reaction = await client.wait_for('reaction_add', timeout=timelimit, check=check)
    except asyncio.TimeoutError as e:
        await message.edit(embed=discord.Embed(title=f"Time out!", description=f"The answer was: `{correct[1]}`", colour=0xe67a7a))
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
        if pre+1 == useranswer:
            await message.edit(embed=discord.Embed(title="Correct!", description=f"The answer was: `{correct[1]}`.", colour=0x7ae687))
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
        else:
            await message.edit(embed=discord.Embed(title="Wrong!", description=f"The answer was: `{correct[1]}`.", colour=0xe67a7a))
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()

@client.command(name='reload')
@commands.is_owner()
async def _reload(ctx, cog="all"):
    async with ctx.typing():
        if cog == "all":
            e = discord.Embed(title=f"Reloading {cog}...", description=f"Reloading Cog: {cog}")
            msg = await ctx.send(embed=e)
            for filename in os.listdir('idiotbot/cogs'):
                if filename.endswith('.py'):
                    client.unload_extension(f'cogs.{filename[:-3]}')
            await msg.edit(embed=discord.Embed(title=f"Unloaded {cog}...", description=f"Unloaded Cog: {cog}"))
            for filename in os.listdir('idiotbot/cogs'):
                if filename.endswith('.py'):
                    client.load_extension(f'cogs.{filename[:-3]}')
            await msg.edit(embed=discord.Embed(title=f"Loaded {cog}...", description=f"Loaded Cog: {cog}"))
        else:
            try:
                client.unload_extension(f"cogs.{cog}")
                msg = await ctx.send(f"Cog: {cog} unloaded.")
                client.load_extension(f"cogs.{cog}")
                await msg.edit(content=f"Cog: {cog} reloaded successfuly.")
            except commands.ExtensionNotFound:
                await ctx.send("Could not find Cog: {cog}.")


for filename in os.listdir('idiotbot/cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(token)
