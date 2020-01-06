# Logging System
import discord
import logging
import traceback
import sys

# Initializes the logger
logFormatter = logging.Formatter('[%(asctime)s][%(name)s] %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
discordLogger = logging.getLogger('discord')
discordLogger.setLevel(logging.INFO)

# discord.log handler
fileHandler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
fileHandler.setFormatter(logFormatter)
discordLogger.addHandler(fileHandler)


# Some modifications to make prints write to the log
class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files: # for every print
            f.write(obj) # write to console
            if not obj == "\n":
                discordLogger.info(obj) # logs to file

    def flush(self):
        for f in self.files: f.flush()
        for h in discordLogger.handlers: h.flush()


backup = sys.stdout # sys.stdout = backup to revert back to printing to console only
sys.stdout = Tee(sys.stdout)


def log(message="", print_to_console=False, type="info"):
    """ Logs a message """
    logger = {
        "critical": discordLogger.critical,
        "error": discordLogger.error,
        "warning": discordLogger.warning,
        "info": discordLogger.info,
        "debug": discordLogger.debug
    }

    if type is "trace":
        discordLogger.error(traceback.format_exc())
    elif print_to_console:
        temp = sys.stdout
        sys.stdout = backup # turns off auto-logging prints
        print(message)
        logger[type](message)
        sys.stdout = temp # turns auto-logging prints back on
    else:
        logger[type](message)
