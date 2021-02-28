import discord, asyncio, aiosqlite3
from discord.ext import commands
global green, red
green = 0x7ae19e
red = 0xdf4e4e

async def getGuildPrefix(guild_id):
    db = await aiosqlite3.connect('idiotbot.db')
    cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (guild_id,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row[0]

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def help(self, ctx):
        if ctx.invoked_subcommand == None:
            e = discord.Embed(title=f"Help - {ctx.author.name if ctx.author.nick == None else ctx.author.nick}",
                            description=f"Idiot bot is a simple bot that I've been working on for a bit. Here are some commands for it.", color=0x7ae19e)
            e.add_field(name="Fun", value="Embed, Game, Quiz, Jesuslaser, Roll")
            e.add_field(name="Moderation", value="Starboard, Purge, Note, Kick, Ban, Tempban")
            e.add_field(name="Other", value="TTS, Skin")
            e.add_field(name='Tags', value='Add|Create|Make, Search, List, Edit, Delete|Remove|Kill')
            e.set_footer(
                text=f"Use {await getGuildPrefix(ctx.guild.id)}help <command> to get more info on a command.", icon_url=e.Empty)
            await ctx.reply(embed=e)


    @help.command(name="skin")
    async def help_skin(self, ctx):
        e = discord.Embed(title=f"Help - Skin", description=f"Use {await getGuildPrefix(ctx.guild.id)}skin <Minecraft Username> to get the skin of a minecraft user. Be warned that discord sometimes takes a while to update, if this is the case just right click the image and open in browser.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="embed")
    async def help_embed(self, ctx):
        e = discord.Embed(title="Help - Embed", description=f"Use {await getGuildPrefix(ctx.guild.id)}embed <title> <description> to send an embed message. This area would be the description. You can also add an image to your message and it will be sent in the embed.", color=0x7ae19e)
        await ctx.send(embed=e)


    #@help.command(name="game")
    #async def help_game(self, ctx):
    #    e = discord.Embed(title="Help - Game",
    #                    description="WIP. Will not Work.", color=0x7ae19e)
    #    await ctx.send(embed=e)


    @help.command(name="quiz")
    async def help_quiz(self, ctx):
        e = discord.Embed(title="Help - Quiz",
                        description="A simple quiz/trivia. You can suggest questions any time you like.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.group(name="starboard")
    async def help_starboard(self, ctx):
        if ctx.invoked_subcommand == None:
            e = discord.Embed(title="Help - Starboard", description=f"A simple way of adding a starboard to your server. Add a starboard channel, and then use {getGuildPrefix(ctx.guild.id)}starboard add to do a quick setup. More info is available with {await getGuildPrefix(ctx.guild.id)}starboard. Long setup is a WIP.", color=0x7ae19e)
            await ctx.send(embed=e)


    @help_starboard.command(name="remove")
    async def help_starboard_remove(self, ctx):
        e = discord.Embed(title="Help - Starboard - Remove",
                        description=f"Use {await getGuildPrefix(ctx.guild.id)}starboard remove to remove starboard from your server.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help_starboard.command(name="add")
    async def help_starboard_add(self, ctx):
        e = discord.Embed(title="Help - Starboard - Add",
                        description=f"Use {await getGuildPrefix(ctx.guild.id)}starboard add to add a starboard to your server.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="roll")
    async def help_roll(self, ctx):
        e = discord.Embed(title="Help - Roll", description=f"Use {await getGuildPrefix(ctx.guild.id)}roll <NdN> to roll a certain number of dice with a certain number of faces. For example, 3d6 would roll three six-sided dice.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="purge")
    async def help_purge(self, ctx):
        e = discord.Embed(title="Help - Purge",
                        description=f"Use {await getGuildPrefix(ctx.guild.id)}purge <limit> [channel] [reason] to clear a certain amount of messages.", color=green)
        await ctx.send(embed=e)


    @help.command(name="jesuslaser")
    async def help_jesuslaser(self, ctx):
        e = discord.Embed(title="Help - Jesuslaser",
                        description=f"Use {await getGuildPrefix(ctx.guild.id)}jesuslaser <target> to jesus laser them.", color=0x7ae19e)
        await ctx.send(embed=e)

    @help.command(name='tts')
    async def help_tts(self, ctx):
        e = discord.Embed(title='Help - TTS', description=f'--- THIS IS A PRIVATE COMMAND --- Use {await getGuildPrefix(ctx.guild.id)}tts <Voice Channel Name/ID (In quotes if it has a space)> <Message> -- This may take a second.', color=green)
        await ctx.send(embed=e)

    @help.group(name='note')
    async def help_note(self, ctx):
        e = discord.Embed(title='Help - Note', description='Notes are for adding a note to a user for things such as warns or previous actions.', color=green)
        e.add_field(name='Help - Note - Get', value='Get notes for a user')
        e.add_field(name='Help - Note - Add', value='Add a note to a user')
        e.add_field(name='Help - Note - Remove', value='Remove a note from a user')
        await ctx.send(embed=e)

    @help_note.command(name='add')
    async def help_note_add(self, ctx):
        e = discord.Embed(title='Help - Note - Add', description=f'Use {await getGuildPrefix(ctx.guild.id)}note add <USER> <NOTE> - Add a note to a user. This will persist across all servers that stupid idiot bot is in. This is only accessible to members with the administrator permission.', color=green)
        await ctx.send(embed=e)

    @help_note.command(name='get')
    async def help_note_get(self, ctx):
        e = discord.Embed(title="Help - Note - Get", description=f"Get all of a user's notes. Use {await getGuildPrefix(ctx.guild.id)}note get <USER>", color=green)
        await ctx.send(embed=e)

    @help_note.command(name='remove')
    async def help_note_remove(self, ctx):
        e = discord.Embed(title='Help - Note - Remove', description=f'Use {await getGuildPrefix(ctx.guild.id)}note remove <USER> <NOTE> - Remove a note from a user.', color=green)
        await ctx.send(embed=e)

    @help.command(name='tempban')
    async def help_tempban(self, ctx):
        e = discord.Embed(title='Help - tempban',
         description=f'Use {await getGuildPrefix(ctx.guild.id)}tempban <USER> <TIME> - Ban a member for the specified amount of time. This uses the same format as the remind command, d - days, h - hours, m - minutes, and s - seconds. For example, {getGuildPrefix(ctx.guild.id)}tempban {self.bot.mention} 3d 5h 6m 3s to ban for 3 days, 5 hours, 6 minutes, and 3 seconds.',
          color=green)
        await ctx.send(embed=e)
    
    @help.command(name='kick')
    async def help_kick(self, ctx):
        e = discord.Embed(title='Help - Kick', description=f'Use {await getGuildPrefix(ctx.guild.id)}kick <USER> [REASON] - Kicks a user from the server. Reason defaults to "**You were kicked. ¯\\_(ツ)_/¯**"', color=green)
        await ctx.send(embed=e)

    @help.command(name='ban')
    async def help_ban(self, ctx):
        e = discord.Embed(title='Help - Ban', description=f'Use {await getGuildPrefix(ctx.guild.id)}kick <user> [REASON] - Bans a user from the server. Reason defaults to "**You were banned. ¯\\_(ツ)_/¯**"',
        color=green)
        await ctx.send(embed=e)

    @help.group(name='tag')
    async def help_tag(self, ctx):
        if ctx.invoked_subcommand == None:
            e = discord.Embed(title='Help - Tag', description=f'Use {await getGuildPrefix(ctx.guild.id)}tag <tag name> to retrieve a tag.', color=green)
            e.add_field(name='Tag - Add|Create|Make', value='Create a Tag')
            e.add_field(name='Tag - Search', value='Search for a Tag')
            e.add_field(name='Tag - List', value='Get a List of Tags')
            e.add_field(name='Tag - Edit', value='Edit a Tag')
            e.add_field(name='Tag - Delete|Remove|Kill', value='Delete a Tag')
            await ctx.send(embed=e)

    @help_tag.command(name='add', aliases=['create', 'make'])
    async def help_tag_add(self, ctx):
        e = discord.Embed(title='Help - Tag - Add|Create|Make', description=f'Use {await getGuildPrefix(ctx.guild.id)}tag add|create|make <name> <value> to make a tag with the name and value specified. Images/Media are not currently supported.', color=green)
        await ctx.send(embed=e)

    @help_tag.command(name='search')
    async def help_tag_search(self, ctx):
        e = discord.Embed(title='Help - Tag - Search', description=f'Use {await getGuildPrefix(ctx.guild.id)}tag search <query> to search for a tag.', color=green)
        await ctx.send(embed=e)

    @help_tag.command(name='list')
    async def help_tag_list(self, ctx):
        e = discord.Embed(title='Help - Tag - List', description=f'Use {await getGuildPrefix(ctx.guild.id)}tag list to get a list of all tags on the server.', color=green)
        await ctx.send(embed=e)

    @help_tag.command(name='edit')
    async def help_tag_edit(self, ctx):
        e = discord.Embed(title='Help - Tag - Edit', description=f'Use {await getGuildPrefix(ctx.guild.id)}tag edit <name> <value> to edit a tag you made.', color=green)
        await ctx.send(embed=e)

    @help_tag.command(name='delete', aliases=['remove', 'kill'])
    async def help_tag_delete(self, ctx):
        e = discord.Embed(title='Help - Tag - Delete|Remove|Kill', description=f'Use {await getGuildPrefix(ctx.guild.id)}tag delete|remove|kill <name> to delete one of your tags.', color=green)
        await ctx.send(embed=e)

def setup(client):
    client.add_cog(Help(client))
