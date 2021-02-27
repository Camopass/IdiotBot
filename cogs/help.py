import discord, asyncio
from discord.ext import commands
global green, red
green = 0x7ae19e
red = 0xdf4e4e

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
            e.set_footer(
                text="Use ?help <command> to get more info on a command.", icon_url=e.Empty)
            await ctx.reply(embed=e)


    @help.command(name="skin")
    async def help_skin(self, ctx):
        e = discord.Embed(title=f"Help - Skin", description="Use ?skin <Minecraft Username> to get the skin of a minecraft user. Be warned that discord sometimes takes a while to update, if this is the case just right click the image and open in browser.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="embed")
    async def help_embed(self, ctx):
        e = discord.Embed(title="Help - Embed", description="Use ?embed <title> <description> to send an embed message. This area would be the description. You can also add an image to your message and it will be sent in the embed.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="game")
    async def help_game(self, ctx):
        e = discord.Embed(title="Help - Game",
                        description="WIP. Will not Work.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="quiz")
    async def help_quiz(self, ctx):
        e = discord.Embed(title="Help - Quiz",
                        description="A simple quiz/trivia. You can suggest questions any time you like.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.group(name="starboard")
    async def help_starboard(self, ctx):
        if ctx.invoked_subcommand == None:
            e = discord.Embed(title="Help - Starboard", description="A simple way of adding a starboard to your server. Add a starboard channel, and then use ?starboard add to do a quick setup. More info is available with ?starboard. Long setup is a WIP.", color=0x7ae19e)
            await ctx.send(embed=e)


    @help_starboard.command(name="remove")
    async def help_starboard_remove(self, ctx):
        e = discord.Embed(title="Help - Starboard - Remove",
                        description="Use ?starboard remove to remove starboard from your server.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help_starboard.command(name="add")
    async def help_starboard_add(self, ctx):
        e = discord.Embed(title="Help - Starboard - Add",
                        description="Use ?starboard add to add a starboard to your server.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="roll")
    async def help_roll(self, ctx):
        e = discord.Embed(title="Help - Roll", description="Use ?roll <NdN> to roll a certain number of dice with a certain number of faces. For example, 3d6 would roll three six-sided dice.", color=0x7ae19e)
        await ctx.send(embed=e)


    @help.command(name="purge")
    async def help_purge(self, ctx):
        e = discord.Embed(title="Help - Purge",
                        description="Use ?purge <limit> [channel] [reason] to clear a certain amount of messages.", color=green)
        await ctx.send(embed=e)


    @help.command(name="jesuslaser")
    async def help_jesuslaser(self, ctx):
        e = discord.Embed(title="Help - Jesuslaser",
                        description="Use ?jesuslaser <target> to jesus laser them.", color=0x7ae19e)
        await ctx.send(embed=e)

    @help.command(name='tts')
    async def help_tts(self, ctx):
        e = discord.Embed(title='Help - TTS', description='--- THIS IS A PRIVATE COMMAND --- Use ?tts {Voice Channel Name/ID (In quotes if it has a space)} {Message} -- This may take a second.', color=green)
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
        e = discord.Embed(title='Help - Note - Add', description='Use ?note add <USER> <NOTE> - Add a note to a user. This will persist across all servers that stupid idiot bot is in. This is only accessible to members with the administrator permission.', color=green)
        await ctx.send(embed=e)

    @help_note.command(name='get')
    async def help_note_get(self, ctx):
        e = discord.Embed(title="Help - Note - Get", description="Get all of a user's notes. Use ?note get <USER>", color=green)
        await ctx.send(embed=e)

    @help_note.command(name='remove')
    async def help_note_remove(self, ctx):
        e = discord.Embed(title='Help - Note - Remove', description='Use ?note remove <USER> <NOTE> - Remove a note from a user.', color=green)
        await ctx.send(embed=e)

    @help.command(name='tempban')
    async def help_tempban(self, ctx):
        e = discord.Embed(title='Help - tempban',
         description=f'Use ?tempban <USER> <TIME> - Ban a member for the specified amount of time. This uses the same format as the remind command, d - days, h - hours, m - minutes, and s - seconds. For example, ?tempban {self.bot.mention} 3d 5h 6m 3s to ban for 3 days, 5 hours, 6 minutes, and 3 seconds.',
          color=green)
        await ctx.send(embed=e)
    
    @help.command(name='kick')
    async def help_kick(self, ctx):
        e = discord.Embed(title='Help - Kick', description='Use ?kick <USER> [REASON] - Kicks a user from the server. Reason defaults to "**You were kicked. ¯\\_(ツ)_/¯**"', color=green)
        await ctx.send(embed=e)

    @help.command(name='ban')
    async def help_ban(self, ctx):
        e = discord.Embed(title='Help - Ban', description='Use ?kick <user> [REASON] - Bans a user from the server. Reason defaults to "**You were banned. ¯\\_(ツ)_/¯**"',
        color=green)
        await ctx.send(embed=e)

    

def setup(client):
    client.add_cog(Help(client))
