# "Fun" Commands, typically generators and search queries
import discord
from discord.ext import commands
from builtins import bot
import asyncio
import aiohttp
from io import BytesIO
import re
import requests
import random
from bs4 import BeautifulSoup
import markovify


def convert_to_url(url):

    # Use regex to remove anything that isn't a number or letter
    url = re.sub(r"[^\w\s]", '', url)

    # Substitute spaces with a '+' symbol
    url = re.sub(r"\s+", '+', url)

    return url



## Markov Chains
def tomarkov(string, states):
    """Returns a randomly generated sentence from the string provided"""

    # Build the model
    string_model = markovify.NewlineText(string, retain_original=False, state_size=states)

    # Construct the requested sentence(s)
    markov_string = ""
    for i in range(random.randint(1,5)): # 1 to 5 sentences are strung together
        markov_string += str(string_model.make_sentence(tries=15)) + " "

    # Return the final string
    return markov_string;

@bot.command(pass_context=True)
@commands.cooldown(1,12, commands.BucketType.channel)
async def markov(ctx, numOfMsgs=500, state_size=2):
    """ Generates a Markov Chain from recent messages."""

    await bot.send_typing(ctx.message.channel)

    if (numOfMsgs <= 50000 and numOfMsgs > 1): # to prevent overflow and exceptions
        log = bot.logs_from(ctx.message.channel, limit=numOfMsgs) # grabs last n messages

        # Put all of the valid messages together as a single string
        string = ""
        async for i in log: # for every message in the log
            if (i.author != bot.user) and (not "c|" in i.clean_content):
                string += i.clean_content + "\n"

        # Send results
        await bot.send_typing(ctx.message.channel)
        await bot.send_message(ctx.message.channel, tomarkov(string, state_size) )
    else:
        await bot.send_message(ctx.message.channel,"❌ | **That number is invalid! Try something else.**")

@markov.error
async def markov(error,ctx):
    print(">>",ctx.message.author,"attempted to run markov, but failed:",error)
    await bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))



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
    print(error)
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
