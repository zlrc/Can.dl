# Overlay commands.
import discord
from discord.ext import commands
from builtins import bot
from math import floor
import asyncio
import aiohttp
from io import BytesIO
from PIL import Image
import os
import random
from wax.logger import log
from wax.helpers import convert_to_url, get_img, abs_path, islambda

class Overlay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.overlay_list = [
                            "thereiam"
                            ]



    @commands.command(pass_context=True)
    @commands.guild_only()
    async def overlays(self, ctx):
        """ Lists available overlay commands. """
        bot = self.bot
        m = "🗒️ | **Available Overlays:**\n```"

        for i in self.overlay_list:
            m += i + ", "

        msg = m.rstrip(", ") + "```"
        await bot.send_typing(ctx.message.channel)
        await bot.send_message(ctx.message.channel,msg)



    def add_overlay(self, source_img, overlay_path, top_left=None, bottom_right=None):
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
            return discord.File(BytesIO(buffer.getvalue()), filename="overlay.png")



    def paste_overlay(self, bg_img, overlay_path, coordinates, scale_multiplierX=1, scale_multiplierY=1):
        """
        Pastes the overlay onto a base image like a sticker.

        This is different from add_overlay() in that the overlay is being
        resized instead, which is preferred for ones that don't act like
        a "frame" for the base image (e.g. picture-in-picture / facecam).

        Parameters
        ----------
        bg_img : BytesIO
            bytes object containing base image to put the overlay on, obtained through get_img(ctx)
        overlay_path : str
            relative filepath of overlay image
        coordinates : tuple, can be int or lambda
            coordinates for the top-left corner of the overlay image.
            to pass a lambda - the function must contain another tuple of parameters (bg_width, overlay_width) for x,
            and height for y.
        scale_multiplierX : int, optional
            a fraction of the background image's HEIGHT to scale the overlay width down to
        scale_multiplierY : int, optional
            a fraction of the background image's HEIGHT to scale the overlay height down to

        Returns
        -------
        BytesIO
            a bytes object containing the resulting image.
        """
        bg = Image.open(bg_img).convert("RGBA")
        bg_width, bg_height = bg.size

        overlay = Image.open(abs_path(overlay_path)).convert("RGBA")
        temp = overlay.resize( (int(bg_height*scale_multiplierX), int(bg_height*scale_multiplierY)) )
        o_width, o_height = temp.size

        x = coordinates[0]
        y = coordinates[1]

        if islambda(x):
            x = coordinates[0]((bg_width, o_width))

        if islambda(y):
            y = coordinates[1]((bg_height, o_height))

        bg.paste(temp,(x,y),temp)
        temp.close()

        # Send the final product
        with BytesIO() as buffer:
            bg.save(buffer,"PNG") # saves generated image to buffer
            bg.close()
            return discord.File(BytesIO(buffer.getvalue()), filename="overlay.png")



    ## Individual functions for each command
    @commands.command(pass_context=True)
    @commands.guild_only()
    async def thereiam(self, ctx):
        """spongehand.png"""
        async with ctx.message.channel.typing():
            file = self.add_overlay(await get_img(ctx),"../db/images/overlays/spongehand.png")
        await ctx.message.channel.send(file=file)



    ## Error Handler(s)
    @thereiam.error
    async def overlay_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await self.bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
        else:
            log(">> overlay command error: {}".format(error), True, type="error")
            log(type="trace")
            await self.bot.send_message(ctx.message.channel,"🔍 | **Couldn't find image!**")




def setup(bot):
    bot.add_cog(Overlay(bot))
