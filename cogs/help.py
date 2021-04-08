import aiosqlite3
import discord
import os
from discord.ext import commands

import idiotlibrary
from idiotlibrary import red, green, name

'''
TODO

-- Add group help command

'''

async def getGuildPrefix(guild):
    if guild == None:
        return '?'
    else:
        guild_id = guild.id
        db = await aiosqlite3.connect('idiotbot.db')
        cursor = await db.execute('SELECT prefix FROM prefixes WHERE author_id = ?', (guild_id,))
        row = await cursor.fetchone()
        await cursor.close()
        await db.close()
        return row[0]


class HelpCmd(commands.MinimalHelpCommand):
    def get_bot_help_signature(self, command):
        return command.qualified_name

    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        embed = discord.Embed(
            title="Categories", description=f"`Prefix: {self.clean_prefix}`", color=green)
        things = []
        for cog, _ in mapping.items():
            cog_name = getattr(cog, "qualified_name", "No Category")
            if cog_name in ['Jishaku', 'Help', 'BotLoop']:
                continue
            things.append(cog_name)
        things = ' \n -- '.join(things[:-1])
        embed.description = f'Prefix: `{self.clean_prefix}` ``` -- {things}```'
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=self.get_command_signature(command),
            color=green,
            description=command.description.format(self.clean_prefix)
        )
        alias = command.aliases
        if alias:
            embed.add_field(
                name="Aliases", value=", ".join(alias), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        commands = cog.get_commands()
        res = []
        for command in commands:
            res.append(command.name)
        commands = ' \n -- '.join(res)
        embed = discord.Embed(title=f'Cog: {cog.qualified_name}', description=f'``` -- {commands}```', color=green)
        await self.get_destination().send(embed=embed)



class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = HelpCmd()


def setup(client):
    client.add_cog(Help(client))

if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:\workspace\idiotbot\idiot bot.py"')
