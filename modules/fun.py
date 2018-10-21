# "Fun" Commands, typically generators and search queries
import discord
from discord.ext import commands
from builtins import bot
import asyncio
import aiohttp
from io import BytesIO
import re
import requests
from bs4 import BeautifulSoup

def convert_to_url(url):

    # Use regex to remove anything that isn't a number or letter
    url = re.sub(r"[^\w\s]", '', url)

    # Substitute spaces with a '+' symbol
    url = re.sub(r"\s+", '+', url)

    return url


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


@bot.command(pass_context=True)
async def trope(ctx, *,args=None):
    """
    Returns a random tv tropes page.
    """
    await bot.send_typing(ctx.message.channel)

    if not args:

        # Opens up a random page through a special url, saves it as the variable: "url"
        async with aiohttp.get("http://tvtropes.org/pmwiki/randomitem.php?p=1") as url:
            await bot.send_message(ctx.message.channel, "{}".format(url.url))
