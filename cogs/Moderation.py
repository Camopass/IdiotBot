import aiosqlite3
import asyncio
import datetime
import discord
import sqlite3
from discord.ext import commands

global green, red
green = 0x7ae19e
red = 0xdf4e4e


# import IdiotLibrary
# from IdiotLibrary import IdiotLib


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int = 10, channel: discord.ext.commands.TextChannelConverter = None, *,
                    reason=None):
        if channel is None:
            await ctx.channel.purge(limit=limit + 1)
        else:
            await channel.purge(limit=limit + (1 if channel == ctx.channel else 0))
        e = discord.Embed(
            title=f"Channel #{ctx.channel.name if channel is None else channel.name} has been purged of {limit} messages.",
            description="No reason provided" if reason is None else reason, color=0xe67a7a)
        await ctx.send(embed=e)

    @commands.group()
    async def note(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(title="Add notes to a user for later, this is serverwide.",
                                               description="A moderator can add notes to a user and save them for later. This could be previous offenses or just any sort of note. Must be less than 1000 characters."))

    @note.command(name="get")
    async def note_get(self, ctx, user: discord.Member):
        conn = sqlite3.connect('idiotbot.db')
        c = conn.cursor()
        data = c.execute("SELECT * FROM notes WHERE user = ?", (user.id,))
        conn.commit()
        conn.close()
        e = discord.Embed(
            title=f"Notes for {user.name}", description=f"Notes for {user.name}", color=0x7ae19e)
        for row in data:
            e.add_field(name=f"Note for {user.name}", value=row[1])
        await ctx.send(embed=e)

    @note.command(name="add")
    @commands.has_permissions(administrator=True)
    async def note_add(self, ctx, user: discord.Member = None, *, note: str = None):
        conn = sqlite3.connect('idiotbot.db')
        c = conn.cursor()
        if user is None:
            e = discord.Embed(title="You have to give it a user you idiot",
                              description="Mention the person you are adding the note to jeez.", color=0x7ae19e)
            await ctx.send(embed=e)
        elif note is None:
            e = discord.Embed(title="Need to add a note man",
                              description="Dude if you want to add a note to a user you gotta give me the note. It's common sense dude, what ar you? British?",
                              color=0x7ae19e)
        else:
            e = discord.Embed(title="Adding note to user...",
                              description="Please wait for SQL to catch up...", color=0x7ae19e)
            message = await ctx.send(embed=e)
            async with ctx.typing():
                c.execute("INSERT INTO notes (user, note) VALUES (?, ?)", (user.id, note))
                conn.commit()
                conn.close()
            e = discord.Embed(
                title=f"Added note to **{user.name}**", description=f"Added the note: `{note}` to user: `{user.name}`",
                color=0x7ae19e)
            await message.edit(embed=e)

    @note.command(name='remove')
    @commands.has_permissions(administrator=True)
    async def note_remove(self, ctx, user: discord.Member = None, *, note: str = None):
        conn = sqlite3.connect('idiotbot.db')
        c = conn.cursor()
        if user is None:
            e = discord.Embed(title="You forgot the user you moron!",
                              description="Maybe mention the person whose notes you want to remove?", color=0x7ae19e)
            await ctx.send(embed=e)
        elif note is None:
            e = discord.Embed(title="You gotta have the note you want to remove the note!",
                              description="Add the note you want to remove you moron!", color=0x7ae19e)
        else:
            e = discord.Embed(
                title=f"Removing note from **{user.name}**...",
                description=f"Removing note: `{note}` from user: `{user.name}`", color=0x7ae19e)
            message = await ctx.send(embed=e)
            async with ctx.typing():
                c.execute("DELETE FROM notes WHERE user = ? AND note = ?", (user.id, note))
                conn.commit()
                conn.close()
            e = discord.Embed(
                title="Done.", description=f"Removed note from **{user.name}**", color=0x7ae19e)
            await message.edit(embed=e)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = "You were kicked. ¯\\_(ツ)_/¯"):
        try:
            await user.kick(reason=reason)
            e = discord.Embed(title=f"User: {user.name} kicked.",
                              description=f"The user **{user.name}** has been kicked by {ctx.author.mention} for the reason: ```{reason}```",
                              color=green)
            await ctx.send(embed=e)
        except discord.Forbidden as e:
            e = discord.Embed(title="Error",
                              description="I do not have permission to kick that member. Try giving me the **Kick Members** role, or putting my role higher on the role list.",
                              color=red)
            await ctx.send(embed=e)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            e = discord.Embed(title="Error",
                              description="You must have the permission: **Kick Members** to use this command.",
                              color=red)
            await ctx.send(embed=e)
        elif isinstance(error, commands.BadArgument):
            e = discord.Embed(title="Error",
                              description="Could not find that user. Please either mention or use the ID of the user you want to kick.",
                              color=red)
            await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = "You were banned. ¯\\_(ツ)_/¯"):
        try:
            await user.ban(reason=reason)
            e = discord.Embed(title=f"User: {user.name} banned.",
                              description=f"The user **{user.name}** has been banned by {ctx.author.mention} for the reason: ```{reason}```",
                              color=green)
            await ctx.send(embed=e)
        except discord.Forbidden as e:
            e = discord.Embed(title="Error",
                              description="I do not have permission to ban that member. Try giving me the **ban Members** role, or putting my role higher on the role list.",
                              color=red)
            await ctx.send(embed=e)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            e = discord.Embed(title="Error",
                              description="You must have the permission: **ban Members** to use this command.",
                              color=red)
            await ctx.send(embed=e)
        elif isinstance(error, commands.BadArgument):
            e = discord.Embed(title="Error",
                              description="Could not find that user. Please either mention or use the ID of the user you want to ban.",
                              color=red)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, user: discord.Member, *arg):
        args = arg
        if args is None:
            await ctx.send("Must pass arguments. I cannot understand that timestamp.")
        else:
            seconds = 0
            for argument in args:
                if argument.endswith("d"):
                    days = argument.split("d")[0]
                    seconds += int(days) * 86400
                if argument.endswith("h"):
                    hours = argument.split("h")[0]
                    seconds += int(hours) * 3600
                if argument.endswith("m"):
                    minutes = argument.split("m")[0]
                    seconds += int(minutes) * 60
                if argument.endswith("s"):
                    seconds2 = argument.split("s")[0]
                    seconds += int(seconds2)
            try:
                await user.ban(reason=f"You were Temp-Banned for {str(datetime.timedelta(seconds=seconds))}")
                e = discord.Embed(title=f"User: **{user.name}** tempbanned",
                                  description=f"Temporarily Banned **{user.name}** for {str(datetime.timedelta(seconds=seconds))}",
                                  color=green)
                await ctx.send(embed=e)
                await asyncio.sleep(seconds)
                await user.unban()
            except discord.Forbidden:
                e = discord.Embed(title="Error",
                                  description="I do not have permission to ban that member. Try giving me the **ban Members** role, or putting my role higher on the role list.",
                                  color=red)
                await ctx.send(embed=e)

    @commands.group()
    async def mute(self, ctx, user: discord.Member):
        conn = sqlite3.connect('idiotbot.db')
        c = conn.cursor()
        data = c.execute('SELECT * FROM mutes WHERE guild_id = ?', (ctx.guild.id,))
        rows = []
        for row in data:
            rows.append(row)
        if not rows:
            e = discord.Embed(title=f"Error",
                              description=f"Could not find any mute roles for the server: {ctx.guild.name}. You can use `?mute role add <ROLE MENTION>` to add a mute role. All roles will be applied to muted members.",
                              color=red)
            await ctx.send(embed=e)
        else:
            muteroles = c.execute('SELECT role_id FROM mutes WHERE guild_id = ?', (ctx.guild.id,))
            for role in muteroles:
                print(role)

    @mute.group(name='role')
    async def mute_role(self, ctx):
        conn = sqlite3.connect('idiotbot.db')
        c = conn.cursor()
        data = c.execute('SELECT role_id FROM mutes WHERE guild_id = ?', (ctx.guild.id,))
        for role in data:
            print(role)

    @mute_role.command(name='add')
    @commands.has_permissions(administrator=True)
    async def mute_role_add(self, ctx, *roles):
        nroles = []
        print(roles)
        for role in roles:
            nroles.append(await commands.RoleConverter().convert(ctx, role))
        for role in nroles:
            await ctx.send(role.name)

    @commands.group()
    async def rr(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title='Reaction Roles', description='Add Reaction Roles to your server!', color=green)
            await ctx.send(embed=e)

    @rr.command(name='add', aliases=['make', 'create'])
    async def rr_add(self, ctx, role:discord.Role=None, channel:discord.TextChannel=None):
        if role is None:
            return await ctx.send('Please mention a role.')
        elif channel is None:
            await ctx.send('No channel specified. Using current channel.', delete_after=10.0)
            channel = ctx.channel
        message = await channel.send(embed=discord.Embed(title=f'Reaction Role for {role.mention}', description=f'React here for the role **{role.name}**!'), color=green)
        db = await aiosqlite3.connect('idiotbot.db')
        await db.execute('INSERT INTO ReactionRoles VALUES (?, ?)', (role.id, message.id))
        await db.commit()
        await db.close()

    @rr.command(name='remove', aliases=['delete', 'kill', 'rm'])
    async def rr_remove(self, ctx, message:discord.Message=None):
        if message is None:
            message = ctx.message.reference
            message = await self.bot.get_channel(message.channel_id).fetch_message(message.message_id)
        db = await aiosqlite3.connect('idiotbot.db')
        data = await db.execute('SELECT message_id from ReactionRoles WHERE message_id=?', (message.id,))
        e = 0
        async for row in data:
            e += 1
        if e == 0:
            await ctx.send('This is not a reaction role, idiot.')
        else:
            await db.execute('DELETE FROM ReactionRoles WHERE message_id=?', (message.id,))
            await message.delete()
        await db.commit()
        await db.close()


def setup(client):
    print("Cog 'Moderation' Ready.")
    client.add_cog(Moderation(client))