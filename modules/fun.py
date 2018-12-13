# "Fun" Commands, typically generators and search queries
import discord
from discord.ext import commands
from builtins import bot
from math import floor
import asyncio
import aiohttp
from io import BytesIO
import re
import requests
import random
from bs4 import BeautifulSoup
from PIL import Image
import markovify
import os


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

def convert_to_url(url):

    # Use regex to remove anything that isn't a number or letter
    url = re.sub(r"[^\w\s]", '', url)

    # Substitute spaces with a '+' symbol
    url = re.sub(r"\s+", '+', url)

    return url

async def get_img(ctx):
    """Returns the most recent attachment posted to the channel"""

    log = bot.logs_from(ctx.message.channel, 50) # check last 50 messages
    async for i in log:
        if i.attachments: # if the message has an attachment
            async with aiohttp.get(i.attachments[0]['url']) as r: # get attachment url
                if r.status == 200:
                    return BytesIO(await r.read())

def abs_path(path):
    """Returns absolute path of file given"""
    script_dir = os.path.dirname(__file__) # absolute path of fun.py
    rel_path = path # relative path
    return os.path.join(script_dir, rel_path) # absolute path of file



## Markov Chains
def tomarkov(string):
    """Returns a randomly generated sentence from the string provided"""

    # Generate a random state size between 2 and 4
    #states = random.randint(2,4)

    # Build the model
    string_model = markovify.NewlineText(string, retain_original=True, state_size=2)

    # Construct the requested sentence(s)
    markov_string = ""
    for i in range(random.randint(1,5)): # 1 to 5 sentences are strung together
        markov_string += str(string_model.make_sentence(tries=100)) + " "

    # Return the final string
    if "None" in markov_string:
        return "❌ | **Error! Failed to generate markov chain, post some more before trying again.**"
    else:
        return markov_string;

async def markovuser(message, member, target_channel):
    """Runs when c|markov is targeted to a particular user"""
    log = bot.logs_from(target_channel, 5000) # grabs last n messages

    # Put all of the valid messages together as a single string
    string = ""
    async for i in log: # for every message in the log
        if (i.author.id == member.id) and (not "c|" in i.clean_content):
            string += i.clean_content + "\n"

    # Create an embed to simulate a user quote
    embed = discord.Embed(color=member.color, description=tomarkov(string))
    embed.set_author(name=member.display_name, icon_url=member.avatar_url[:-15])

    # Send results
    await bot.send_typing(message.channel)
    await bot.send_message(message.channel,embed=embed)

async def markovchannel(message, target_channel):
    """Runs when c|markov is targeted to a particular channel"""
    log = bot.logs_from(target_channel, 1000) # grabs last n messages

    # Put all of the valid messages together as a single string
    string = ""
    async for i in log: # for every message in the log
        if (i.author != bot.user) and (not "c|" in i.clean_content):
            string += i.clean_content + "\n"

    # Send results
    await bot.send_typing(message.channel)
    await bot.send_message(message.channel, tomarkov(string) )

@bot.command(pass_context=True)
@commands.cooldown(2,20, commands.BucketType.channel)
async def markov(ctx, user=None, chan=None):
    """ Generates a Markov Chain from recent messages."""

    print(">> {} requested a markov chain, processing...".format(ctx.message.author)) # log command usage

    # Convert channel to an object we can work with
    if chan: # sets default channel if one isn't provided
        chan = ctx.message.server.get_channel(chan[2:-1])
    else:
        chan = ctx.message.channel

    await bot.send_typing(ctx.message.channel)

    def user_is(type, u): # bypasses TypeError exception when user=None
        if type == "channel":
            try:
                if ctx.message.server.get_channel(u[2:-1]):
                    return True
                else:
                    return False
            except TypeError:
                return False
        elif type == "member":
            try:
                if ctx.message.server.get_member_named(user):
                    return True
                else:
                    return False
            except TypeError:
                return False

    # Compile a string of messages that meet the criteria
    if ctx.message.mentions: # checks if a mention was used
        await markovuser(ctx.message, ctx.message.mentions[0], chan)
    elif user_is("member", user): # if mention wasn't used to find user
        await markovuser(ctx.message, ctx.message.server.get_member_named(user), chan)
    elif user_is("channel", user): # if a channel was given without user mention
        await markovchannel(ctx.message, ctx.message.server.get_channel(user[2:-1]))
    else:
        log = bot.logs_from(ctx.message.channel, 800) # grabs last n messages

        # Put all of the valid messages together as a single string
        string = ""
        async for i in log: # for every message in the log
            if (i.author != bot.user) and (not "c|" in i.clean_content):
                string += i.clean_content + "\n"

        # Send results
        await bot.send_typing(ctx.message.channel)
        await bot.send_message(ctx.message.channel, tomarkov(string) )

@markov.error
async def markov(error,ctx):
    print(">> {} attempted to run c|markov, but failed: {}".format(ctx.message.author,error))
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        await bot.send_message(ctx.message.channel,"❌ | **Error! Proper Syntax:** `c|markov @user #channel` **(user and channel optional)**")



## Stack Overflow Lookup
@bot.command(pass_context=True)
async def stack(ctx, *,args):
    """
    Searches Stack Overflow and returns the top result.
    """
    search_url = requests.get("https://stackoverflow.com/search?q=" + convert_to_url(args))
    soup = BeautifulSoup(search_url.content, "html.parser")
    await bot.send_typing(ctx.message.channel)

    # Find the first <a> element that has the URL we need, convert to a url.
    top_result = soup.find('a', {'class': "question-hyperlink"})
    result_url = "https://stackoverflow.com" + top_result.get('href')

    await bot.send_message(ctx.message.channel, "{}".format(result_url))

@stack.error
async def stack(error,ctx):
    print(">> c|stack: {}".format(error))
    await bot.send_message(ctx.message.channel,"❌ | **Please enter a valid search query!**")



## TV Tropes
@bot.command(pass_context=True)
async def trope(ctx, *,args=None):
    """
    Returns a random tv tropes page.
    """
    await bot.send_typing(ctx.message.channel)

    if not args:

        # Opens up a random page through a special url, saves it as the variable: "url"
        async with aiohttp.get("http://tvtropes.org/pmwiki/randomitem.php?p="+str(random.randint(1,9999999999))) as url:
            await bot.send_message(ctx.message.channel, "{}".format(url.url))



## Overlay Commands
@bot.command(pass_context=True)
async def pequod(ctx):
    """
    Adds the motherbase.png overlay to the most recent image posted
    (this command is hidden from the help menu)
    """
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
async def kojima(ctx):
    """therealfinaldestination.png"""
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

@kojima.error
@mariod.error
@pequod.error
@jared.error
@flag.error
@snake.error
async def overlay_error(error,ctx):
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
    else:
        print(">> overlay command error: {}".format(error))
        await bot.send_message(ctx.message.channel,"🔍 | **Couldn't find image!**")
