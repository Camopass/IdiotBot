#Stupid idiot bot V1.0
import discord, requests, json, math, random, asyncio, os, platform
from win10toast import ToastNotifier
toaster = ToastNotifier()
from mojang import MojangAPI
from discord.ext import commands
if str(platform.system()) == 'Windows':
    dir = 'E:\\workspace\\idiotbot\\token.txt'
elif str(platform.system()) == "Linux":
    dir = '/home/camopass/discord_token.txt'
else:
    raise(f"Error: System {platform.system()} not recognized.")
with open (dir, "r") as myfile:
    token = str(myfile.readlines()[0])
    print(f"Using token {token}")
intents = discord.Intents.all()
client = commands.Bot(command_prefix=['?', 'hey idiot, '], intents=intents, case_insensitive=True)
client.remove_command('help')
invischaracter = "ㅤ"

class CustomCtx:                                                        # Custom context for the jump_url detection
    def __init__(self, message, bot, guild, channel, author):
        self.message = message
        self.bot = bot
        self.guild = guild
        self.channel = channel
        self.author = author

def get_starboards():
    with open("E:\\workspace\\idiotbot\\starboards.txt", 'r') as f:
        words = f.read()
        return(eval(str(words)))

words = ["person", "world", "hand", "woman", "place", "point", "government", "company", "number", "problem", "little"]

q = list(questions.keys())

@client.event
async def on_ready():
    print('Bot is ready.')

'''@client.event
async def on_command_error(ctx, error):
    e = discord.Embed(title="You broke me you idiot",
                      description=f"You gave me an error, what are you? British? ```{error}```", color=0x7ae19e)
    await ctx.send(embed=e)
    await client.get_channel(808831381592866847).send(f"Bot: Stupid Idiot Bot ```{error}```")'''

@client.event                                                         # This lets you see a message that has been linked
async def on_message(message):
    if "https://canary.discord.com/channels/" in message.content and not message.author.bot:                                       #  This detects if a canary link is in the message
        url = f"https://canary.discord.com/channels/{message.content.split('https://canary.discord.com/channels/', 2)[1]}"         #  Get the URL for the message
        if " " in url:                                                                                                             #  ---------------------------
            url = url.split(" ", 2)[0]                                                                                             #  ---------------------------
        #await message.channel.send(url)                                                                                           #  ---------------------------
        context = CustomCtx(message, client, message.guild, message.channel, message.author)                                       #  Create a context object so we can use MessageConverter()
        nmessage = await discord.ext.commands.MessageConverter().convert(context, url)                                             #  Fetch the message from the link, using the url and the custom context
        e = discord.Embed(title=f"Message referenced by {message.author}", description=nmessage.content, color=0x7ae19e)           #  Create the embed object
        e.set_author(name=nmessage.author.name)                                                                                    #  Add the name of the person who sent the message to the embed
        if len(nmessage.attachments) != 0:                                                                                         #  Detect if there is an attachment on the linked message
            if nmessage.attachments[0].height != 0:                                                                                #  Is the attachment an image?
                e.set_image(url=nmessage.attachments[0].url)                                                                       #  If yes, add the image to the embed
        await message.channel.send(embed=e)                                                                                        #  Send the embed
    elif "https://discord.com/channels/" in message.content and not message.author.bot:                                            #  The same thing as above but for regular client jump urls
        url = f"https://discord.com/channels/{message.content.split('https://discord.com/channels/', 2)[1]}"
        if " " in url:
            url = url.split(" ", 2)[0]
        #await message.channel.send(url)
        context = CustomCtx(message, client, message.guild,
                            message.channel, message.author)
        nmessage = await discord.ext.commands.MessageConverter().convert(context, url)
        e = discord.Embed(
            title=f"Message referenced by {message.author}", description=nmessage.content, color=0x7ae19e)
        e.set_author(name=nmessage.author.name)
        if len(nmessage.attachments) != 0:
            if nmessage.attachments[0].height != 0:
                e.set_image(url=nmessage.attachments[0].url)
        await message.channel.send(embed=e)
    # The same thing as above but for regular client jump urls
    elif "https://discordapp.com/channels/" in message.content and not message.author.bot:
        url = f"https://discordapp.com/channels/{message.content.split('https://discordapp.com/channels/', 2)[1]}"
        if " " in url:
            url = url.split(" ", 2)[0]
        #await message.channel.send(url)
        context = CustomCtx(message, client, message.guild,
                            message.channel, message.author)
        nmessage = await discord.ext.commands.MessageConverter().convert(context, url)
        e = discord.Embed(
            title=f"Message referenced by {message.author}", description=nmessage.content, color=0x7ae19e)
        e.set_author(name=nmessage.author.name)
        if len(nmessage.attachments) != 0:
            if nmessage.attachments[0].height != 0:
                e.set_image(url=nmessage.attachments[0].url)
        await message.channel.send(embed=e)
    if message.content == "jump_url":
        if message.reference != None:
            nmessage = await client.get_channel(message.reference.channel_id).fetch_message(
                message.reference.message_id)
            await message.channel.send(nmessage.jump_url)
    await client.process_commands(message)




def get_factors(num:int):
    t = int(num)
    r = []
    for i in range(t):
        if int(num) % t == 0:
            r.append((t, int(num)/t))
        t -= 1
    return(r)

class GameApple:
    def __init__(self):
        self.x = random.randint(0, 7)
        self.y = random.randint(0, 7)
        self.Pos = (self.y * 8) + self.x
    def randomize(self):
        self.x = random.randint(0, 7)
        self.y = random.randint(0, 7)
        self.Pos = (self.y * 8) + self.x

class Snake:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.Pos = 0
    def moveX(self, change):
        self.x += change
        self.Pos = (self.y * 8) + self.x
    def moveY(self, change):
        self.y += change
        self.Pos = (self.y * 8) + self.x

@client.event
async def on_raw_reaction_add(payload):
    user = payload.member
    if str(payload.emoji) == "\U00002b50":
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
                channel = client.get_channel(eval(str(get_starboards()[str(message.guild.id)])))
                e = discord.Embed(title="Message", description=message.content, colour=0xf2d202, url=message.jump_url)
                e.set_author(name=f"{user.name} - {count}/{members}", icon_url=user.avatar_url)
                if len(message.attachments) != 0:
                    embed = message.attachments[0]
                    e.set_image(url=embed.url)
                await channel.send(message.jump_url, embed=e)
                await message.add_reaction("\U00002705")
                eternalstarboard = client.get_channel(805931186785878047)
                await eternalstarboard.send(embed=e)
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
                channel = client.get_channel(eval(str(get_starboards()[str(message.guild.id)])))
                e = discord.Embed(title="Message", description=message.content, colour=0xf2d202, url=message.jump_url)
                e.set_author(name=f"{message.author.name} - {count}/{members}", icon_url=message.author.avatar_url)
                if len(message.attachments) != 0:
                    embed = message.attachments[0]
                    e.set_image(url=embed.url)
                await channel.send(message.jump_url, embed=e)
                await message.add_reaction("\U00002705")
                eternalstarboard = client.get_channel(805931186785878047)
                await eternalstarboard.send(embed=e)


'''@client.event
async def on_message(message):
    if not message.author.bot:
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
                        break
    await client.process_commands(message)'''

@client.command()
async def idiot(ctx):
    await ctx.send("I'm an idiot, you moron.")

@client.group()
async def game(ctx):
    if ctx.invoked_subcommand == None:
        e = discord.Embed(title="Stupid Idiot Game", description="A stupid game made by an moron on an idiot bot.", colour=0x7ae19e)
        e.add_field(name="start", value="Use ?game start to start a new game, moron")
        e.add_field(name="end", value="Use ?game end to end the game, you moron")
        e.add_field(name="Controls", value="They're in the reactions, you moron")
        await ctx.send(embed=e)

@game.command()
async def start(ctx, Borders=True):
    startMessage = await ctx.send("Setting up the game (idiot)")
    GameArray = [
{0 : [0, 0], 1 : [0, 0], 2 : [0, 0], 3 : [0, 0], 4 : [0, 0], 5 : [0, 0], 6 : [0, 0], 7 : [0, 0]},
{8 : [0, 0], 9 : [0, 0], 10: [0, 0], 11: [0, 0], 12: [0, 0], 13: [0, 0], 14: [0, 0], 15: [0, 0]},
{16: [0, 0], 17: [0, 0], 18: [0, 0], 19: [0, 0], 20: [0, 0], 21: [0, 0], 22: [0, 0], 23: [0, 0]},
{24: [0, 0], 25: [0, 0], 26: [0, 0], 27: [0, 0], 28: [0, 0], 29: [0, 0], 30: [0, 0], 31: [0, 0]},
{32: [0, 0], 33: [0, 0], 34: [0, 0], 35: [0, 0], 36: [0, 0], 37: [0, 0], 38: [0, 0], 39: [0, 0]},
{40: [0, 0], 41: [0, 0], 42: [0, 0], 43: [0, 0], 44: [0, 0], 45: [0, 0], 46: [0, 0], 47: [0, 0]},
{48: [0, 0], 49: [0, 0], 50: [0, 0], 51: [0, 0], 52: [0, 0], 53: [0, 0], 54: [0, 0], 55: [0, 0]},
{56: [0, 0], 57: [0, 0], 58: [0, 0], 59: [0, 0], 60: [0, 0], 61: [0, 0], 62: [0, 0], 63: [0, 0]}
]
    SnakePos = Snake()
    Apple = GameApple()
    GameArray[Apple.y][(Apple.y*8)+Apple.x][0] = 1  #create apple
    GameArray[0][0][0] = 3  #create snake
    await startMessage.edit(content="OOO-------")
    GameData = []
    yIndex = 0
    for i in GameArray:
        rows = []
        for x in i:
            if i[x][0] == 0:
                rows.append(":black_large_square:")
            elif i[x][0] == 1:
                rows.append(":apple:")
            elif i[x][0] == 2:
                rows.append(":green_square:")
            elif i[x][0] == 3:
                rows.append(":flushed:")
            yIndex += 1
        GameData.append(rows)
    await startMessage.edit(content="OOOOOO----")
    Game = ""
    i = ""
    score = 0
    for x in GameData:
        e = "".join(x)
        Game = f"{Game}{e}\n"
    await startMessage.edit(content="Finished Game Setup.")
    e = discord.Embed(title = f"Snake - {score} points", description = Game, colour=0x69f077)
    e.set_author(name= ctx.author.name, icon_url=str(ctx.author.avatar_url))
    msg = await ctx.send(embed=e)
    await msg.add_reaction("\U00002b05")
    await msg.add_reaction("\U000027a1")
    await msg.add_reaction("\U00002b06")
    await msg.add_reaction("\U00002b07")
    await startMessage.delete()
    def check(reaction, user):
        return(user == ctx.author)  #["\U00002b05", "\U000027a1", "\U00002b06", "\U00002b07"]
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=6.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(title= "Too slow!", description= f"Hey, {ctx.author.mention}, You ran out of time to respond! Use ?game start to try again!", colour= 0x69f077))
    else:
        if str(reaction) == "\U00002b05": #left
            SnakeDir, DirName = 4, "left"
        if str(reaction) == "\U000027a1": #right
            SnakeDir, DirName = 2, "right"
        if str(reaction) == "\U00002b06": #up
            SnakeDir, DirName = 1, "up"
        if str(reaction) == "\U00002b07": #down
            SnakeDir, DirName = 3, "down"
        await reaction.remove(ctx.author)

        await ctx.send(DirName + ' ' + user.name, delete_after=3)

        GameArray[SnakePos.y][SnakePos.y][0] = 2
        GameArray[SnakePos.y][SnakePos.y][1] = score

        if SnakeDir in [2, 4]:
            SnakePos.moveX(-1 * (SnakeDir/2 - 2))
        else:
            SnakePos.moveY(1 if SnakeDir==1 else -1)

        Apple.randomize()
        GameArray[Apple.y][(Apple.y*8)+Apple.x][0] = 1  #create apple
        GameArray[SnakePos.x][SnakePos.y][0] = 3  #create snake
        await startMessage.edit(content="OOO-------")
        GameData = []
        yIndex = 0

        for i in GameArray:
            rows = []
            for x in i:
                if i[x][0] == 0:
                    rows.append(":black_large_square:")
                elif i[x][0] == 1:
                    rows.append(":apple:")
                elif i[x][0] == 2:
                    rows.append(":green_square:")
                elif i[x][0] == 3:
                    rows.append(":flushed:")
                yIndex += 1
            GameData.append(rows)
        await startMessage.edit(content="OOOOOO----")
        Game = ""
        i = ""
        for x in GameData:
            e = "".join(x)
            Game = f"{Game}{e}\n"

        e = discord.Embed(title = f"Snake - {score} points", description = Game, colour=0x69f077)
        e.set_author(name= ctx.author.name, icon_url=str(ctx.author.avatar_url))
        await msg.edit(embed=e)

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
        reaction, user = await client.wait_for('reaction_add', timeout=timelimit, check=check)
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

@client.command()
async def factors(ctx, num:int=None):
    if num == None:
        await ctx.send("Must have a number.")
    else:
        answer = get_factors(num)
        i = ""
        for tuple in answer:
            i += str(tuple)
        await ctx.send(i)

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
