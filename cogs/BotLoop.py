import discord, aiosqlite3, datetime
from discord.ext import commands
from discord.ext import tasks

class BotLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot loop is looping.')

    @tasks.loop(minutes=30)
    async def birthLoop(self, ctx):
        now = datetime.datetime.now().strftime("%m/%d")
        async with aiosqlite3.connect('idiotbot.db') as db:
            async with db.execute('SELECT * FROM birthdays WHERE date=?', (now,)) as cursor:
                async for row in cursor:
                    try:
                        user = self.bot.get_user(row[0])
                        await user.send('Happy Birthday!')
                    except Exception as e:
                        print(e)

def setup(client):
    client.add_cog(BotLoop(client))