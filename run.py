# Bot created by zlrc on github
import discord
from discord.ext import commands
import builtins
import os
import json
import sqlite3
from sqlite3 import Error
import datetime

client = discord.Client()
bot = commands.Bot(command_prefix='c|')
builtins.bot = bot



## Logging System
import logging

logFormatter = logging.Formatter('[%(asctime)s][%(name)s] %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
discordLogger = logging.getLogger('discord')
discordLogger.setLevel(logging.INFO)

# discord.log handler
fileHandler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
fileHandler.setFormatter(logFormatter)
discordLogger.addHandler(fileHandler)

# Modifying the command line to write prints to file
import sys

class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files: # for every print
            f.write(obj) # write to console
            if not obj == "\n":
                discordLogger.info(obj) # logs to file

backup = sys.stdout # sys.stdout = backup to revert back to printing to console only
sys.stdout = Tee(sys.stdout)



## Loading up the config, refer to the readme file if missing.
with open("config.json") as cfg:
    config = json.load(cfg)

TOKEN = config["token"]
ownerID = config["ownerID"]

import modules.main
import modules.admin
import modules.utility
import modules.fun
import modules.overlay



## Setting up database for tracking usage frequency
usage_db = sqlite3.connect(os.path.realpath('db/bot_usage.db'))

try: # set up a table if one doesn't exist already
    c = usage_db.cursor()
    c.execute('''CREATE TABLE usage_data
             (month integer, day integer, hour integer, minute integer, weekday text)''')
    usage_db.commit()
    print(">> No usage data table found, generating a new one...")
except:
    pass

def record_invoke():
    """Records current date and time to database"""
    current = datetime.datetime.now()
    weekday = datetime.datetime.today().weekday()
    w = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    data = (current.month, current.day, current.hour, current.minute, w[weekday])

    usage_db = sqlite3.connect(os.path.realpath('db/bot_usage.db'))
    c = usage_db.cursor()

    c.execute('INSERT INTO usage_data VALUES (?,?,?,?,?)', data)
    usage_db.commit()
    usage_db.close()
    #print(data)



## Now we're ready to start up the bot
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    # Check if debug mode is enabled
    if config["debugModeEnabled"]:
        print("*** DEBUG MODE IS ENABLED ***")
        await bot.change_presence(status="invisible")

        @bot.check
        def debug_owner_check(ctx):
            """Prevents everyone but the bot owner from executing commands while debug mode is enabled"""
            return ctx.message.author.id == ownerID
    else:
        @bot.check
        def usage_counter(ctx):
            record_invoke()
            return True


bot.run(TOKEN)
