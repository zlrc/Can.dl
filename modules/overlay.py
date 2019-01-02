# Overlay commands. There's a lot of them, so they're part of their own module
import discord
from discord.ext import commands
from builtins import bot
from math import floor
import asyncio
import aiohttp
from io import BytesIO
from PIL import Image
import os
from modules.fun import convert_to_url, get_img, abs_path

overlay_list = ["pequod",
                "snake",
                "mariod",
                "makarov",
                "kojima",
                "jared",
                "thereiam",
                "sonic",
                "sm64",
                "trogun",
                "flag"]


def add_overlay(source_img, overlay_path, top_left=None, bottom_right=None):
    """Adds given overlay to provided base image, returns as bytes object"""

    script_dir = os.path.dirname(__file__) # absolute path of fun.py
    rel_path = overlay_path # relative path of the overlay image
    abs_file_path = os.path.join(script_dir, rel_path) # absolute path of overlay image

    overlay = Image.open(abs_file_path).convert("RGBA") # overlay image
    source = Image.open(source_img).convert("RGBA") # base image before editing
    o_width, o_height = overlay.size # stores width and height of overlay image
    s_width, s_height = source.size # stores width and height of source

    if top_left and bottom_right: # if coordinates for a frame is given
        f_width = bottom_right[0] - top_left[0] # specified frame width
        f_height = bottom_right[1] - top_left[1] # specified frame height

        n_height = int(floor(s_height*(f_width/s_width))) # calculate height of base image
        if n_height < f_height:
            n_height = f_height

        base = source.resize( (f_width, n_height) ) # resize to width of frame
        bg = Image.new("RGBA", (o_width, o_height), (255, 255, 255))
        bg.paste(base,top_left,base)
        bg.paste(overlay,(0,0),overlay)
        base_final = bg.crop((0,0,o_width,o_height)) # crop to overlay
    else:
        n_height = int(floor(s_height*(o_width/s_width))) # calculate height of base image
        if n_height < o_height:
            n_height = o_height

        base = source.resize( (o_width, n_height) ) # resizes to width of overlay
        base.paste(overlay,(0,0),overlay) # pastes overlay onto the base image
        base_final = base.crop((0,0,o_width,o_height)) # crop to overlay

    overlay.close()
    source.close()

    with BytesIO() as buffer:
        base_final.save(buffer,"PNG") # saves generated image to buffer
        base_final.close()
        return BytesIO(buffer.getvalue())



## Individual functions for each command
@bot.command(pass_context=True)
async def pequod(ctx):
    """motherbase.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/motherbase.png")
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="pequod.png")

@bot.command(pass_context=True)
@commands.cooldown(1,5, commands.BucketType.channel)
async def snake(ctx):
    """snake-binoculars.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/snake-binoculars.png",(0,281),(499, 560))
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="snake.png")

@bot.command(pass_context=True)
async def mariod(ctx):
    """mario-odyssey.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/mario-odyssey.png")
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="mariod.png")

@bot.command(pass_context=True)
@commands.cooldown(1,5, commands.BucketType.channel)
async def makarov(ctx):
    """makarov.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/makarov.png",(15,34),(396, 312))
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="makarov.png")

@bot.command(pass_context=True)
@commands.cooldown(1,5, commands.BucketType.channel)
async def kojima(ctx):
    """kojima1.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/kojima1.png",(47,249),(176, 412))
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="kojima.png")

@bot.command(pass_context=True)
async def jared(ctx):
    """jared.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/jared.png")
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="jared.png")

@bot.command(pass_context=True)
async def thereiam(ctx):
    """spongehand.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/spongehand.png")
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="thereiam.png")

@bot.command(pass_context=True)
async def sonic(ctx):
    """sonic.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/sonic.png")
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="sonic.png")

@bot.command(pass_context=True)
@commands.cooldown(1,5, commands.BucketType.channel)
async def sm64(ctx):
    """SuperMario64.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/SuperMario64.png",(157,31),(483, 377))
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="sm64.png")

@bot.command(pass_context=True)
async def trogun(ctx):
    """troggun.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/troggun.png")
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="trogun.png")

@bot.command(pass_context=True)
@commands.cooldown(1,5, commands.BucketType.channel)
async def flag(ctx):
    """tumblr flag overlay"""
    top_left = Image.open(abs_path("../db/images/overlays/flag1.png")).convert("RGBA") # "Your post has been flagged"
    top_right = Image.open(abs_path("../db/images/overlays/flag2.png")).convert("RGBA") # "Review"
    source = Image.open(await get_img(ctx)).convert("RGBA") # base image before editing
    banner = Image.new("RGBA", (source.size[0], 50), (252, 75, 57))

    source.paste(banner,(0,0),banner)
    source.paste(top_left,(0,0),top_left)
    source.paste(top_right,(source.size[0]-top_right.size[0],0),top_right)
    banner.close()
    top_left.close()
    top_right.close()

    with BytesIO() as buffer:
        source.save(buffer,"PNG") # saves generated image to buffer
        source.close()
        img = BytesIO(buffer.getvalue())

        await bot.send_typing(ctx.message.channel)
        await bot.send_file(ctx.message.channel, fp=img, filename="flag.png")



## Error Handler(s)
@pequod.error
@snake.error
@mariod.error
@makarov.error
@kojima.error
@jared.error
@thereiam.error
@sonic.error
@sm64.error
@trogun.error
@flag.error
async def overlay_error(error,ctx):
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
    else:
        print(">> overlay command error: {}".format(error))
        await bot.send_message(ctx.message.channel,"🔍 | **Couldn't find image!**")
