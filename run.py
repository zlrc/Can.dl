# Main file to run the bot from. Created by zlrc on github.
from wax.bot import Candl
from wax import logger
import json

# Loading up the config, refer to the readme file if missing.
with open("config.json") as cfg:
    config = json.load(cfg)

# Start the bot up
bot = Candl(config=config, help_command=None)
bot.run()
