import discord, asyncio, os, sys
from discord.ext import commands
from PIL import Image, ImageFilter
from io import BytesIO

# (111, 213), (302, 403)


global green, red
green = 0x7ae19e
red = 0xdf4e4e


class HiddenPrints:
    async def __aenter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout



class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Put a person\'s face on a wanted poster!')
    async def wanted(self, ctx, member:discord.Member=None):
        if member == None:
            member = ctx.author
        
        wanted = Image.open(r'E:\workspace\idiotbot\Wanted.jpg')
        asset = member.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((192, 192))
        wanted.paste(pfp, (111, 213))
        wanted.save('WantedPfp.jpg')
        image = discord.File(r'E:\workspace\WantedPfp.jpg', filename='WantedPfp.jpg')
        e = discord.Embed(title=f'Wanted: **{member.name}**', color=green)
        e.set_image(url='attachment://WantedPfp.jpg')
        await ctx.send(file=image, embed=e)

    @commands.command(description='Resize an image.')
    async def resize(self, ctx, width:int, height:int, emote:discord.Emoji=None):
        image = None

        async def size(image0):
            w0, h0 = image0.size
            image0 = image0.resize((width, height))
            image0.save('ResizeImage.png')
            image0 = discord.File(
                'ResizeImage.png', filename='ResizeImage.png')
            e = discord.Embed(
                title=f'Resized from: {w0}, {h0} to {width}, {height}', color=green)
            e.set_image(url='attachment://ResizeImage.png')
            await ctx.send(file=image0, embed=e)

        if len(ctx.message.attachments) == 0:
            if emote == None:
                return await ctx.send(embed=discord.Embed(title='Error', description='Please attach an image to resize.'), color=red)
            else:
                image = await emote.url.save('Emote.png')
                image = Image.open(r'E:\workspace\Emote.png')
                await size(image)
        elif width >= 1921 or height >= 1081:
            return await ctx.send(embed=discord.Embed(title='Error', description='Please choose a size under 1920x1080', color=red))
        elif ctx.message.attachments[0].height == None:
            return await ctx.send(embed=discord.Embed(title='Error', description='Please attach an image you idiot.', color=red))
        elif ctx.message.attachments[0].height >= 2001 or ctx.message.attachments[0].width >= 2001:
            return await ctx.send(embed=discord.Embed(title='Error', description='Please attach an image under 2000x2000.', color=red))
        else:
            image = ctx.message.attachments[0]
            image = BytesIO(await image.read())
            await size(Image.open(image))

    @commands.command(description='Jesuslaser something.')
    async def jesuslaser(self, ctx, *, target: str):
        msg = await ctx.send("Targeting.")
        await asyncio.sleep(1)
        await msg.edit(content="Targeting..")
        await asyncio.sleep(1)
        await msg.edit(content="Targeting...")
        await asyncio.sleep(1)
        await msg.edit(content=f"Target: **{target}** found. Deploying Jesus laser.")
        await asyncio.sleep(1)
        image = discord.File(
            open(r'E:\workspace\idiotbot\jesuslaser.jpg', 'rb'))
        await ctx.send(file=image)



def setup(bot):
    bot.add_cog(Images(bot))