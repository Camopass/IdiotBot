### Idiot Bot Library
---
**Functions**

---
> idiotlibrary.trim_str(string, length=2000):

Not a coroutine. This will trim any string down to the specified length.

**Usage**

---
```
>>> from idiotlibrary import trim_str
>>> string = 'String here. This is a string. Striiing.'
>>> print(trim_str(string, 5))
Strin
```

> idiotlibrary.to_string(character):

Coroutine.
This function will transform any character to the \U unicode value.

**Usage**

---
```
>>> from idiotlibrary import to_string
>>> character = '😁'
>>> print(await to_string(character))
\U0001f601
```

> idiotlibrary.convert_emoji(ctx, emoji):

Coroutine.
This fuction will transform an emoji into the discord.py string representation of the emoji. Still a WIP.

> idiotlibrary.get_non_bot_members(guild):

Coroutine.
This function will get the member count of a guild not including bots.

**Usage**

---
```
from idiotlibrary import get_non_bot_members
print(await get_non_bot_members(ctx.guild))
```

> idiotlibrary.get_raw_count(bot, payload):

Couroutine.
This function gets the count of a reaction. This is intended for use in the discord event `on_raw_reaction_add`.

**Usage**

---
```
from idiotlibrary import get_raw_count()
@bot.event
async def on_raw_reaction_add(payload):
    count = get_raw_count(bot, payload)
```

> idiotlibrary.name(member):

Not a coroutine.
This function returns the nickname of a user or the name of the member. It is simple, but mch more efficient than `member.name if member.nick is None else member.nick`.

**Usage**

---
```
>>> from idiotlibrary import name
>>> print(name(guild.me))
Stupid Idiot Bot
>>> person = random.choice(guild.members)
>>> print(name(person))
Paulo
>>> print(person.name)
James
>>> print(person.nick)
Paulo
```

> idiotlibrary.pages_simple(ctx, message, *, max_size=1500, prefix='```', suffix='```', delete_after=True)

Coroutine.
This will take a message and make it into a paginator interface. The goal is simplicity, so all parameters but `ctx` and `message` are optional.

**Usage**

---
```
@bot.command()
async def menu(ctx):
    message = ''
    for i in range(1000):
        message += 'Long message '
    await idiotlibrary.pages_simple(ctx, message)
```

### Classes

---

> idiotlibrary.Menu(page, embed, *, delete_after=False):

A `discord.ext.menus.Menu` interface that takes a list of pages. If `page` is a list of embeds, set embed to `True`.   `delete_after` lets you control if the menu is deleted after being finished with.

**Usage**

---
```
pages = ['Page 1!' '2', '3', '4']
menu = idiotlibrary.Menu(pages, False)
await menu.start(ctx)
```

### Constants

---

> idiotlibrary.red

The red color used for Stupid Idiot Bot

**Value**

---
```
>>> idiotlibrary.red
0xdf4e4e
```

> idiotlibrary.green

The green color used for Stupid Idiot Bot

**Value**

---
```
>>> idiotlibrary.red
0x7ae19e
```

> idiotlibrary.check_mark_emoji

The check mark emoji

**Value**

---
```
>>> idiotlibrary.check_mark_emoji
\U00002705
```

> idiotlibrary.red_x_emoji

The red x emoji

**Value**

---
```
>>> idiotlibrary.check_mark_emoji
\U0000274c
```