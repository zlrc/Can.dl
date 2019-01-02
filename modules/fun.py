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


def convert_to_url(url):

    # Use regex to remove anything that isn't a number or letter
    url = re.sub(r"[^\w\s]", '', url)

    # Substitute spaces with a '+' symbol
    url = re.sub(r"\s+", '+', url)

    return url

async def get_img(ctx):
    """Returns the most recent attachment posted to the channel"""

    # regex to check if there is an image url within the message
    url_regex = r'(\b(?:(?:https?)|(?:ftp)|(?:file)):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*(?:(?:\.jpg)|(?:\.jpeg)|(?:\.png)|(?:\.gif)))'

    log = bot.logs_from(ctx.message.channel, 50) # check last 50 messages
    async for i in log:
        if i.attachments: # if the message has an attachment
            url = i.attachments[0]['url'] # attachment url
        elif re.search(url_regex,i.clean_content,flags=re.IGNORECASE): # look for url using regex
            url = re.search(url_regex,i.clean_content,flags=re.IGNORECASE).group(0)

        try:
            async with aiohttp.get(url) as r: # access the url
                if r.status == 200:
                    return BytesIO(await r.read())
        except:
            pass

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

    # Generate chain from messages, keep trying if there's an error
    msg = tomarkov(string)
    attempts = 1
    while ("❌ |" in msg) and (attempts <= 5):
        print("    >> Failed, trying again... ({}/5)".format(attempts) )
        await bot.send_typing(message.channel)
        log = bot.logs_from(target_channel, 5000+(1000*attempts))
        #start = 5000 + ( 1000*(attempts-1) )

        string = ""
        async for i in log:
            if (i.author.id == member.id) and (not "c|" in i.clean_content):
                string += i.clean_content + "\n"
        msg = tomarkov(string)
        attempts += 1


    # Create an embed to simulate a user quote
    embed = discord.Embed(color=member.color, description=msg)
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
from modules.overlay import overlay_list

@bot.command(pass_context=True)
async def overlays(ctx):
    m = "🗒️ | **Available Overlays:**\n```"

    for i in overlay_list:
        m += i + ", "

    msg = m.rstrip(", ") + "```"
    await bot.send_typing(ctx.message.channel)
    await bot.send_message(ctx.message.channel,msg)
