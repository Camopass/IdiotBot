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
            e.add_field(name="Fun", value="Skin, Embed, Game, Quiz, Jesuslaser")
            e.add_field(name="Server Utility", value="Starboard, Purge")
            e.add_field(name="Random", value="Roll")
            e.set_footer(
                text="Use ?help <command> to get more info on a command.", icon_url=e.Empty)
            await ctx.send(embed=e)


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
                        description="Use ?purge <limit> [channel] [reason] to clear a certain amount of messages.")
        await ctx.send(embed=e)


    @help.command(name="jesuslaser")
    async def help_jesuslaser(self, ctx):
        e = discord.Embed(title="Help - Jesuslaser",
                        description="Use ?jesuslaser <target> to jesus laser them.", color=0x7ae19e)
        await ctx.send(embed=e)

def setup(client):
    client.add_cog(Help(client))
