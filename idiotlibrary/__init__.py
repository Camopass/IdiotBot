import discord
import traceback
from discord.ext import commands, menus

import asyncio

version = '1.0.0'
green = 0x7ae19e
red = 0xdf4e4e
check_mark_emoji = '\U00002705'
red_x_emoji = '\U0000274c'

def test():
    print('Module is loaded.')

def trim_str(string: str, length: int = 2000):
    if len(string) <= length:
        return string
    else:
        trim = len(string) - length
        return string[:-trim]
        #Trims a string

async def to_string(c):
    digit = f'{ord(c):x}'
    return f'\\U{digit:>08}'
# Chr to \U

async def convert_emoji(ctx, emoji):
    try:
        emoji = await commands.EmojiConverter().convert(ctx, emoji)
    except commands.BadArgument:
        emoji = await to_string(emoji)
    finally:
        return str(emoji)
#\U if standard emoji and <:name:id> if custom

async def get_non_bot_members(guild):
    members = 0
    for member in guild.members:
        if not member.bot:
            members += 1
    return members
# This gets the member count of any guild that does not include bot members.

async def get_raw_count(bot, payload):
    try:
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    except discord.errors.NotFound:
        return 0
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

async def pages_simple(ctx, message:str, *, max_size=1500, prefix='```', suffix='```', delete_after=True):
    pages = commands.Paginator(
        prefix=prefix, suffix=suffix, max_size=max_size)
    for line in message.split('\n'):
        pages.add_line(line)
    menu = Menu(pages.pages, False, delete_after=delete_after)
    await menu.start(ctx)

class StarboardEmojiConverter(commands.Converter):
    async def convert(self, ctx, argument):
        return await convert_emoji(ctx, argument)
    

class Menu(menus.Menu):
    def __init__(self, page, embed:bool, *, delete_after=False):
        timeout = 180
        delete_message_after = False
        clear_reactions_after = False
        check_embeds = False
        message = None
        self.timeout = timeout
        self.delete_message_after = delete_message_after
        self.clear_reactions_after = clear_reactions_after
        self.check_embeds = check_embeds
        self._can_remove_reactions = False
        self.__tasks = []
        self._running = True
        self.message = message
        self.ctx = None
        self.bot = None
        self._author_id = None
        self._buttons = self.__class__.get_buttons()
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()
        self.page = page
        self.pagenum = 0
        self.delete_after = delete_after
        self.embed = embed

    async def send_initial_message(self, ctx, channel):
        if self.embed:
            return await channel.send(embed=self.pages[0])
        else:
            return await channel.send(self.page[0] + f'Page {self.pagenum + 1}/{len(self.page)}')
    
    @menus.button('\U000023ea')
    async def on_first(self, payload):
        self.pagenum = 0
        await self.message.edit(content=self.page[self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page)}')

    @menus.button('\U00002b05')
    async def on_back(self, payload):
        if not self.pagenum == 0:
            self.pagenum -= 1
            await self.message.edit(content=self.page[self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page)}')

    @menus.button('\U000027a1')
    async def on_right(self, payload):
        self.pagenum += 1
        await self.message.edit(content=self.page[self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page)}')

    @menus.button('\U000023e9')
    async def on_last(self, payload):
        self.pagenum = len(self.page) - 1
        await self.message.edit(content=self.page[self.pagenum] + f'Page {self.pagenum + 1}/{len(self.page)}')
    
    @menus.button('\U0001f522')
    async def on_select(self, payload):
        await self.message.edit(content='Enter the number of the page you want to go to.')
        msg = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == self.ctx.author and self.channel == self.ctx.channel)
        self.pagenum = int(msg.content)
        await self.message.edit(content=self.page[self.pagenum])

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        await self.message.clear_reactions()
        self.stop()
        if self.delete_after:
            await asyncio.sleep(15)
            await self.message.delete()



if __name__ == '__main__':
    pass