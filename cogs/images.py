import discord
import asyncio
import os
import sys
import aiohttp
import re
from discord.ext import commands
from PIL import Image, ImageFilter
from io import BytesIO

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


class ImageConverter(commands.Converter):
    '''
    Convert any argument into an image if possible.
    This will not work with images attached to the message.
    If you want it to work with images on the message,
    add =None after the argument, then in the function:
        if arg is None:
            arg = await ImageConverter().image(ctx.message)
    '''
    async def convert(self, ctx, argument):
        r = re.search(r'<a?:\w+:\d{18}>', argument)
        if r:
            emoji = await commands.EmojiConverter().convert(ctx, argument)
            asset = emoji.url_as(format='png')
            data = BytesIO(await asset.read())
            return data
        elif re.search(r'https?://.+\.(png|jpg|jpeg)', argument):
            async with aiohttp.ClientSession() as session:
                async with session.get(argument) as resp:
                    if resp.status == 200:
                        return BytesIO(await resp.read())
        else:
            try:
                user = await commands.MemberConverter().convert(ctx, argument)
            except commands.MemberNotFound:
                await ctx.send(f'`{argument}`')
            else:
                avatar = user.avatar_url_as(format='png')
                data = BytesIO(await avatar.read())
                return data
    
    
    async def image(self, message):
        if len(message.attachments) > 0:
            attachment = message.attachments[0]
            if attachment.height is not None:
                return BytesIO(await attachment.read())
        else:
            user = message.author
            avatar = user.avatar_url_as(format='png')
            data = BytesIO(await avatar.read())
            return data



class images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def idiot(self, ctx, image:ImageConverter=None):
        if image is None:
            image = await ImageConverter().image(ctx.message)
        image = discord.File(image, filename='Image.png')
        await ctx.send(file=image)


    @commands.command(description='Put a person\'s face on a wanted poster!')
    async def wanted(self, ctx, *, image:ImageConverter=None):
        if image is None:
            image = await ImageConverter().image(ctx.message)
        pfp = Image.open(image)
        wanted = Image.open(r'E:\workspace\idiotbot\Wanted.png')
        pfp = pfp.resize((192, 192)).convert('RGBA')
        wanted.alpha_composite(pfp, (111, 213))
        im = BytesIO()
        wanted.save(im, 'PNG')
        im = im.getvalue()
        image = discord.File(BytesIO(im), filename='Wanted.png')
        e = discord.Embed(title=f'Wanted', color=green)
        e.set_image(url='attachment://Wanted.png')
        await ctx.send(file=image, embed=e)
    

    @commands.command()
    async def bonk(self, ctx, *, image:ImageConverter=None):
        if image is None:
            image = await ImageConverter().image(ctx.message)
        dog = Image.open(r'E:\workspace\idiotbot\bonk.png')
        pfp = Image.open(image)
        pfp = pfp.resize((206, 206)).convert('RGBA')
        dog.alpha_composite(pfp, (461, 193))
        im = BytesIO()
        dog.save(im, 'PNG')
        im = im.getvalue()
        image = discord.File(BytesIO(im), 'Bonk.png')
        e = discord.Embed(title=f'Bonk', color=green)
        e.set_image(url='attachment://Bonk.png')
        await ctx.send(file=image, embed=e)


    @commands.command(description='Resize an image.')
    async def resize(self, ctx, width:int, height:int, image:ImageConverter=None):
        if image is None:
            image = await ImageConverter().image(ctx.message)
        if width > 2000 or height > 2000 or width < 1 or height < 1:
            return await ctx.send('Invalid Dimensions')

        async def size(image0):
            w0, h0 = image0.size
            image0 = image0.resize((width, height))
            im = BytesIO()
            image0.save(im, 'PNG')
            im = im.getvalue()
            image0 = discord.File(
                BytesIO(im), filename='ResizeImage.png')
            e = discord.Embed(
                title=f'Resized from: {w0}, {h0} to {width}, {height}', color=green)
            e.set_image(url='attachment://ResizeImage.png')
            await ctx.send(file=image0, embed=e)

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
    bot.add_cog(images(bot))


if __name__ == '__main__':
    os.system(r'C:/Users/Cameron/AppData/Local/Programs/Python/Python39/python.exe "e:/workspace/idiotbot/idiot bot.py"')
