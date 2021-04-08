import aiosqlite3
import asyncio
import datetime
import discord
import os
from discord.ext import commands

import idiotlibrary
from idiotlibrary import red, green, red_x_emoji, check_mark_emoji


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Purge a channel of a certain number of messages. WIP: You can specify a certain member to purge the messages from.')
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit:int, person:discord.Member):
        channel = ctx.channel
        await channel.purge(limit=limit + (1 if channel == ctx.channel else 0))
        e = discord.Embed(
        title=f"Channel #{ctx.channel.name if channel is None else channel.name} has been purged of {limit} messages.", color=0xe67a7a)
        await ctx.send(embed=e)

    @commands.group(description='A moderator can add notes to a user and save them for later. This could be previous offenses or just any sort of note. Must be less than 1000 characters.')
    async def note(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(title="Add notes to a user for later, this is serverwide.",
                                               description="A moderator can add notes to a user and save them for later. This could be previous offenses or just any sort of note. Must be less than 1000 characters."))

    @note.command(name="get", description='Get the notes for a user.')
    async def note_get(self, ctx, user: discord.Member):
        async with aiosqlite3.connect('idiotbot.db') as db:
            cursor = await db.execute('SELECT * FROM notes')
        e = discord.Embed(
            title=f"Notes for {user.name}", description=f"Notes for {user.name}", color=0x7ae19e)
        for row in cursor:
            e.add_field(name=f"Note for {user.name}", value=row[1])
        await ctx.send(embed=e)

    @note.command(name="add", description='Add a note to a user.')
    @commands.has_permissions(administrator=True)
    async def note_add(self, ctx, user: discord.Member = None, *, note: str = None):
        async with aiosqlite3.connect('idiotbot.db') as db:
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
                    await db.execute("INSERT INTO notes (user, note) VALUES (?, ?)", (user.id, note))
                    await db.commit()
                e = discord.Embed(
                    title=f"Added note to **{user.name}**", description=f"Added the note: `{note}` to user: `{user.name}`",
                    color=0x7ae19e)
                await message.edit(embed=e)

    @note.command(name='remove', description='Remove a note from a user.')
    @commands.has_permissions(administrator=True)
    async def note_remove(self, ctx, user: discord.Member = None, *, note: str = None):
        async with aiosqlite3.connect('idiotbot.db') as db:
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
                    await db.execute("DELETE FROM notes WHERE user = ? AND note = ?", (user.id, note))
                    await db.commit()
                e = discord.Embed(
                    title="Done.", description=f"Removed note from **{user.name}**", color=0x7ae19e)
                await message.edit(embed=e)

    @commands.command(description='Kick a user from the server.')
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

    @commands.command(description='Ban a user from the server.')
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

    @commands.command(description='Temporarily ban a user from the server. Use {0}tempban [user] [time]. Time is specified using the amount of [days|hours|minutes|seconds] followed by the corresponding suffix [d|h|m|s]')
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

    @commands.group(description='WIP: Mute a user.')
    async def mute(self, ctx):
        e = discord.Embed(title='Mutes', description='You can mute a member with a certain role added to the bot, or you can quick add a role. (WIP)', color=green)
        e.add_field(name='Mute - Role', value='See the roles added to muted members.')
        e.add_field(name='Mute - Role - Add', value='Add a mute role to the server.')
        await ctx.send(embed=e)

    @mute.group(name='role', description='WIP')
    async def mute_role(self, ctx):
        '''conn = sqlite3.connect('idiotbot.db')
        c = conn.cursor()
        data = c.execute('SELECT role_id FROM mutes WHERE guild_id = ?', (ctx.guild.id,))
        for role in data:
            print(role)'''
        pass

    @mute_role.command(name='add', description='WIP: Set a mute role.')
    @commands.has_permissions(administrator=True)
    async def mute_role_add(self, ctx, role:discord.Role):
        async with aiosqlite3.connect('idiotbot.db') as db:
            await db.execute('DELETE FROM mutes WHERE guild_id=?', (ctx.guild.id,))
            await db.execute('INSERT INTO mutes VALUES (?, ?)', (ctx.guild.id, role.id))
            await db.commit()
        e = discord.Embed(title='Set Mute Role', description=f'Set mute role for **{ctx.guild.name}** to {role.mention}.', color=green)
        await ctx.send(embed=e)

    @commands.group(description='WIP: Set a message to give a user a certain role when reacting to a message.')
    async def rr(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title='Reaction Roles', description='Add Reaction Roles to your server!', color=green)
            await ctx.send(embed=e)

    @rr.command(name='add', aliases=['make', 'create'], description='Add a reaction role to the channel. Use {0}rr add [role] [channel]')
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

    @rr.command(name='remove', aliases=['delete', 'kill', 'rm'], description='WIP: Remove a reaction role.')
    async def rr_remove(self, ctx, message:discord.Message=None):
        if message is None:
            message = ctx.message.reference
            message = await self.bot.get_channel(message.channel_id).fetch_message(message.message_id)
        db = await aiosqlite3.connect('idiotbot.db')
        data = await db.execute('SELECT message_id from ReactionRoles WHERE message_id=?', (message.id,))
        e = 0
        async for _ in data:
            e += 1
        if e == 0:
            await ctx.send('This is not a reaction role, idiot.')
        else:
            await db.execute('DELETE FROM ReactionRoles WHERE message_id=?', (message.id,))
            await message.delete()
        await db.commit()
        await db.close()
    
    @commands.command(brief='Create a poll that people can react to.', description='Use {0}poll to create a poll that people can react to. Once you use {0}poll, send messages and add the :white_check_mark: emoji. Send finished when you are done.')
    async def poll(self, ctx, *, poll=None):
        if poll is None:
            e = discord.Embed(
                title='Poll',
                description='Creating poll. What should the poll be about?',
                color=green
            )
            ogmessage = await ctx.send(embed=e)
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            message = await self.bot.wait_for('message', check=check, timeout=60.0)
            del check
            poll = message.content
            e = discord.Embed(
                title='Poll',
                description=f'Nice. The poll is for **{poll}**. Now, what should the options be?',
                color=green
            )
            await ogmessage.edit(embed=e)
        elif poll is not None:
            e = discord.Embed(
                title='Poll',
                description=f'Nice. The poll is for **{poll}**. Now, what should the options be? (use `finished|done|complete|cancel` to stop.',
                color=green
            )
            message = await ctx.send(embed=e)
        options = []
        finished = False
        def checkm(m):
            return m.author == ctx.author and m.channel == ctx.channel
        while finished == False:
            if len(options) >= 4:
                finished = False
            else:
                msg = await self.bot.wait_for('message', check=checkm, timeout=60.0)
                if msg.content.lower() in ['finished', 'done' 'complete', 'cancel']:
                    if msg.content.lower() in ['stop', 'cancel']:
                        return await ctx.send('Cancelled Poll.')
                    if len(options) <= 1:
                        await ctx.send('You need more options than that.')
                    else:
                        finished = True
                        break
                else:
                    e = discord.Embed(
                        title='Option',
                        description=f'Do you want to add the option **{msg.content}**?',
                        color=green
                    )
                    confirm = await ctx.send(embed=e)
                    await confirm.add_reaction(red_x_emoji)
                    await confirm.add_reaction(check_mark_emoji)
                    def checkr(reaction, user):
                        return user == ctx.author and reaction.message == confirm
                    try:
                        reaction, message = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkr)
                    except asyncio.TimeoutError:
                        await ctx.send('Cancelling Poll...', delete_after=10.0)
                        return
                    else:
                        if str(reaction) == check_mark_emoji:
                            options.append(msg.content)
                        else:
                            await ctx.send('Alrighty-o then.')
        description = ''
        numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣']
        for index, option in enumerate(options):
            description += f'{numbers[index+1]}   **{option}**\n'
        e = discord.Embed(
            title=poll,
            description=description,
            color=green
        )
        message = await ctx.send(embed=e)
        e.set_footer(text=f'Poll ID ∙ {message.id}')
        await message.edit(embed=e)
        for index in range(len(options)):
            await message.add_reaction(numbers[index+1])


    @commands.command(description='See the prefix for the server, or set a prefix. If your prefix has spaces at the end, surround it in `"` or `\'`.')
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, *, prefix=None):
        prefix = prefix.strip('\'"')
        if ctx.guild is None:
            e = discord.Embed(
                title='Error', description='You cannot change the prefix in DM\'s. You can only use "?".', color=red)
            await ctx.send(embed=e)
        if prefix is None:
            message = ctx.message
            db = await aiosqlite3.connect('idiotbot.db')
            cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (message.guild.id,))
            row = await cursor.fetchone()
            await cursor.close()
            await db.close()
            prefix = row[0]
            e = discord.Embed(
                title='Prefix', description=f'Current Prefix is `{prefix}`', color=green)
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
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            e = discord.Embed(title='Error', description='Sorry, only a moderator can change the prefix of the bot.',
                            color=red)
            await ctx.send(embed=e)



def setup(client):
    client.add_cog(Moderation(client))

if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:\workspace\idiotbot\idiot bot.py"')
