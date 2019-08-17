# Helper functions used by other files
from io import BytesIO
import aiohttp
import re
import os

def convert_to_url(url):
    """ Makes a search string url-friendly """
    # Use regex to remove anything that isn't a number or letter
    url = re.sub(r"[^\w\s]", '', url)

    # Substitute spaces with a '+' symbol
    url = re.sub(r"\s+", '+', url)

    return url

async def get_img(ctx):
    """Returns the most recent attachment posted to the channel"""

    # regex to check if there is an image url within the message
    url_regex = r'(\b(?:(?:https?)|(?:ftp)|(?:file)):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*(?:(?:\.jpg)|(?:\.jpeg)|(?:\.png)|(?:\.gif)))'

    log = ctx.message.channel.history(limit=50) # check last 50 messages
    async for i in log:
        if i.attachments: # if the message has an attachment
            url = i.attachments[0].url # attachment url
        elif re.search(url_regex,i.clean_content,flags=re.IGNORECASE): # look for url using regex
            url = re.search(url_regex,i.clean_content,flags=re.IGNORECASE).group(0)

        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url) as r: # access the url
                    if r.status == 200:
                        return BytesIO(await r.read())
        except:
            pass

def abs_path(path):
    """Returns absolute path of file given"""
    script_dir = os.path.dirname(__file__) # absolute path of helpers.py
    rel_path = path # relative path
    return os.path.join(script_dir, rel_path) # absolute path of file

def islambda(v):
    """ Checks if v is a lambda function """
    LAMBDA = lambda:0
    return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__
