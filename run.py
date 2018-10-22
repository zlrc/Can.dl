# Bot created by zlrc on github
import discord
from discord.ext import commands
import builtins
import os
import json

client = discord.Client()
bot = commands.Bot(command_prefix='c|')
builtins.bot = bot



## Logging System
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s:%(levelname)s:%(name)s]: %(message)s'))
logger.addHandler(handler)

# Modifying the command line to write prints to file
import sys

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)

f = open('discord.log', 'w')
backup = sys.stdout # sys.stdout = backup to revert back to printing to console only
sys.stdout = Tee(sys.stdout, f)



## Loading up the config, refer to the readme file if missing.
with open("config.json") as cfg:
    config = json.load(cfg)

TOKEN = config["token"]
ownerID = config["ownerID"]

import modules.main
import modules.admin
import modules.utility
import modules.fun



## Now we're ready to start up the bot
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)
