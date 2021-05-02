import discord
from discord.ext import commands

version = '1.0.0'

def test():
    print('Module is loaded.')

def trim_str(string: str, length: int = 2000):
    if len(string) <= length:
        return string
    else:
        trim = len(string) - length
        return string[:-trim]

async def to_string(c):
    digit = f'{ord(c):x}'
    return f'`\\U{digit:>08}`'
# Chr to \U

async def convert_emoji(ctx, emoji):
    try:
        emoji = await commands.EmojiConverter().convert(ctx, emoji)
    except commands.BadArgument:
        emoji = await to_string(emoji)
    finally:
        return f"`{emoji}`"
#\U if standard emoji and <:name:id> if custom

async def get_non_bot_members(guild):
    members = 0
    for member in guild.members:
        if not member.bot:
            members += 1
    return members
# This gets the member count of any guild that does not include bot members.

async def get_raw_count(bot, payload):
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    for reaction in message.reactions:
        if str(reaction.emoji) == str(payload.emoji):
            return reaction.count
    return 0
#Reaction count for on_raw_reaction_add

def name(user):
    if user.nick == None:
        return user.name
    else:
        return user.nick
#This is shorter than user.name if user.nick == None else user.nick



if __name__ == '__main__':
    test()
