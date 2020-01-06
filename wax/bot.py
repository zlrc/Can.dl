# Main startup file for the bot
import discord
from discord.ext import commands
import builtins
import os
import sqlite3
import datetime
from wax.logger import log

class Candl(commands.Bot):

    def __init__(self, *args, **kwargs):
        """ Constructor for the bot class """
        config = kwargs.pop("config", None)

        # Store the configurations
        self.token = config["token"]
        self.ownerID = config["ownerID"]
        self.command_prefix = config["prefix"]
        self.debug_mode = config["debugModeEnabled"]
        self.modules = [key for key in filter(lambda i: config["active_modules"][i], config["active_modules"])]
        self.keys = config["api_keys"]

        # Instantiate the bot
        builtins.bot = super().__init__(command_prefix=self.command_prefix, *args, **kwargs)
        self.init_api_keys()
        self.create_db()
        self.load_cog(*self.modules)



    ### Startup Functions ######################################################
    def run(self):
        """ Connects the bot to discord """
        self.client = discord.Client()
        super().run(self.token)

    async def on_ready(self):
        """ Automatically gets called when the bot is ready for use. """
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------ discord.py v' + discord.__version__ + ' ------')

        # Check if debug mode is enabled
        if self.debug_mode:
            print("*** DEBUG MODE IS ENABLED ***")
            await self.change_presence(status="invisible")
        else:
            @self.check_once # creates an event to record timestamps each invoke
            def usage_counter(ctx):
                self.record_invoke()
                log("Command invoked by {}, processing...".format(ctx.message.author))
                return True

    async def on_message(self, msg):
        """ Runs a few checks before its superclass handles the call """
        if self.debug_mode and await self.is_owner(msg.author) == False: # disables input in debug mode
            return
        else:
            await super().on_message(msg)
            if self.private_cog is not None:
                await self.private_cog.on_message(msg)



    ### Cogs ###################################################################
    def load_cog(self, *cogs):
        """ Loads modules passed through cogs parameter """
        for name in cogs:
            path = "modules." + name
            self.load_extension(path)
            log("Cog Loaded: {}".format(name))
        self.private_cog = self.get_cog("Private")

    def reload_cog(self, name):
        """ Reloads the given modules """
        path = "modules." + name
        self.reload_extension(path)
        print(">> Cog Reloaded: {}".format(name))

    def refresh_cogs(self):
        """ Reloads all enabled modules """
        for name in self.modules:
            path = "modules." + name
            self.reload_extension(path)
            print(">> Cog Reloaded: {}".format(name))



    ### Third-party APIs #######################################################
    def init_api_keys(self):
        """ Initializes APIs using their respective keys. """
        pass



    ### Analytics ##############################################################
    def create_db(self):
        """ Sets up the database that tracks usage frequency """
        usage_db = sqlite3.connect(os.path.realpath('db/bot_usage.db'))

        try: # set up a table if one doesn't exist already
            c = usage_db.cursor()
            c.execute('''CREATE TABLE usage_data
                     (month integer, day integer, hour integer, minute integer, weekday text)''')
            usage_db.commit()
            log(">> No usage data table found, generating a new one...", True, type="warning")
            usage_db.close()
        except:
            pass

    def record_invoke(self):
        """ Records current date and time to database """
        current = datetime.datetime.now()
        weekday = datetime.datetime.today().weekday()
        w = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        data = (current.month, current.day, current.hour, current.minute, w[weekday])

        usage_db = sqlite3.connect(os.path.realpath('db/bot_usage.db'))
        c = usage_db.cursor()

        c.execute('INSERT INTO usage_data VALUES (?,?,?,?,?)', data)
        usage_db.commit()
        usage_db.close()
        log("Invoke has been logged as: {}".format(data), type="debug")



    ### Misc. Functions ########################################################
    async def send_message(self, channel, message=None, **kwargs):
        """ A legacy command that makes updating to rewrite less painful """
        emb = kwargs.pop("embed", None)
        await channel.send(message, embed=emb) if message else await channel.send(embed=emb)

    async def send_typing(self, channel):
        await channel.trigger_typing()
