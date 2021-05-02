import discord
import asyncio
import aiosqlite3
import datetime
import json
import os
from discord.ext import commands
from discord.ext import tasks

config = json.loads(open(r'config.json').read())
databasedir = config['Database Directory']


async def AsyncMap(_list: list, func: callable, args: tuple=None):
    '''
    Run a function for each item in a list as an asynchronous generator.
    The first argument for the function must be the item in the list, any args after that should be put in a tuple.
    '''
    if args:
        for item in _list:
            yield await func(item, *args)
    else:
        for item in _list:
            yield await func(item)

def time_check(task, limit:datetime.timedelta, now:datetime.datetime, time:datetime.datetime):
    diff = time - now
    if diff < datetime.timedelta(seconds=0):
        return 2, task
    if diff < (limit / 2):
        return 1, task
    elif diff < limit:
        return 0, task
    else:
        return (None, None)



class botloop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_ready(self):
        #pylint: disable=no-member
        try:
            self.reminderloop.start()
        except RuntimeError:
            pass
    

    async def send_message(self, user:int, event:str, channel:int, time:datetime.datetime):
        now = datetime.datetime.now()
        if time > now:
            sleep = time - now
            await asyncio.sleep(sleep.total_seconds())
        author = self.bot.get_user(user)
        if author == None:
            #raise RuntimeError('Could not find user.')
            pass
        message = f'{author.mention}, your reminder is over. ```{event}```'
        await self.bot.get_channel(channel).send(message)


    '''@tasks.loop(minutes=30)
    async def birthLoop(self):
        now = datetime.datetime.now().strftime("%m/%d")
        async with aiosqlite3.connect('idiotbot.db') as db:
            async with db.execute('SELECT * FROM birthdays WHERE date=?', (now,)) as cursor:
                async for row in cursor:
                    try:
                        user = self.bot.get_user(row[0])
                        await user.send('Happy Birthday!')
                    except Exception as e:
                        print(e)'''
    
    @tasks.loop(minutes=1)
    async def reminderloop(self):
        async with aiosqlite3.connect(databasedir) as db:
            data = await db.execute('SELECT timeExecuted, event FROM reminders')
            rows = await data.fetchall()
        high = []
        medium = []
        low = []
        task_queue_data = [low, medium, high]
        for item in rows:
            try:
                importance, data = time_check(item[1], datetime.timedelta(
                    minutes=1), datetime.datetime.now(), datetime.datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S.%f'))
            except ValueError:
                importance, data = time_check(item[1], datetime.timedelta(
                    minutes=1), datetime.datetime.now(), datetime.datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S'))
            if data == None:
                continue
            else:
                task_queue_data[importance].append(data)
        task_queue = high + medium + low
        async with aiosqlite3.connect('idiotbot.db') as db:
            for task in task_queue:
                data = await db.execute('SELECT author, event, channel, timeExecuted FROM reminders WHERE event=?', (task,))
                rows = await data.fetchall()
                rows = rows[0]
                try:
                    asyncio.ensure_future(self.send_message(rows[0], rows[1], rows[2], datetime.datetime.strptime(rows[3], '%Y-%m-%d %H:%M:%S.%f')))
                except ValueError:
                    asyncio.ensure_future(self.send_message(rows[0], rows[1], rows[2], datetime.datetime.strptime(rows[3], '%Y-%m-%d %H:%M:%S')))
                await db.execute('DELETE FROM reminders WHERE event = ? AND timeExecuted = ?', (rows[1], rows[3]))
                await db.commit()
    
    @reminderloop.before_loop
    async def before_reminderloop(self):
        await self.bot.wait_until_ready()
            
        


def setup(bot):
    bot.add_cog(botloop(bot))


if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:/workspace/idiotbot/idiot bot.py"')
