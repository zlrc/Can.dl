# Overlay commands. There can be a lot of them, so they're part of their own module
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

overlay_list = ["thereiam",
                #"fake_entry",
                ""]


def add_overlay(source_img, overlay_path, top_left=None, bottom_right=None):
    """
    Adds given overlay to provided base image.

    Parameters
    ----------
    source_img : BytesIO
        bytes object containing base image to put the overlay on, obtained through get_img(ctx)
    overlay_path : str
        relative filepath of overlay image
    top_left : (int, int), optional
        coordinates for the top-left corner of the frame source_img appears in
    bottom_right : (int, int), optional
        coordinates for the bottom-right corner of the frame source_img appears in

    Returns
    -------
    BytesIO
        a bytes object containing the resulting image.
    """

    script_dir = os.path.dirname(__file__) # absolute path of this .py file
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

        y_offset = int(floor((n_height - o_height)/2)) # top-left corner's y-coordinate, for centering on the y-axis
        base = source.resize( (o_width, n_height) ) # resizes to width of overlay
        base.paste(overlay,(0,y_offset),overlay) # pastes overlay onto the base image
        base_final = base.crop((0,y_offset,o_width,o_height+y_offset)) # crop to overlay

    overlay.close()
    source.close()

    with BytesIO() as buffer:
        base_final.save(buffer,"PNG") # saves generated image to buffer
        base_final.close()
        return BytesIO(buffer.getvalue())



## Individual functions for each command
@bot.command(pass_context=True)
async def thereiam(ctx):
    """spongehand.png"""
    file = add_overlay(await get_img(ctx),"../db/images/overlays/spongehand.png")
    await bot.send_typing(ctx.message.channel)
    await bot.send_file(ctx.message.channel, fp=file, filename="thereiam.png")



## Error Handler(s)
@thereiam.error
async def overlay_error(error,ctx):
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
    else:
        print(">> overlay command error: {}".format(error))
        await bot.send_message(ctx.message.channel,"🔍 | **Couldn't find image!**")
