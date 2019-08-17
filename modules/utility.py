# Utility Commands, most come with special configurations and run in the background
import discord
from discord.ext import tasks, commands
import asyncio
import datetime
from wax.helpers import abs_path
from wax.logger import log
from PIL import Image
from io import BytesIO

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timers = {}

    def cog_unload(self):
        if self.timers:
            for i in list(self.timers):
                self.timers.pop(i)


    def generate_banner(color):
        # Convert hex-value to RGB
        h = color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

        # Create image objects
        bg = Image.new("RGBA", (800, 300), rgb)
        text = Image.open(abs_path("../db/images/invite.png")).convert("RGBA")

        bg.paste(text,(0,0),text)
        text.close()
        bg.close()

    async def message_exists(self, channel, id):
        try:
            await self.bot.get_message(channel, id)
            return True
        except:
            return False

    # Countdown
    class CountdownClock():
        def __init__(self, message, title, hh, mm, ss, color, mention):
            self.title = title
            self.message = message
            self.mention_enabled = mention
            self.color = color

            self.hour = int(hh)
            self.minute = int(mm)
            self.second = int(ss)

            self.total_seconds = self.second+(60*self.minute)+(60*60*self.hour)
            self.goal_time = datetime.datetime.now() + datetime.timedelta(seconds=self.total_seconds)
            print(">> {} created a timer for {} seconds".format(message.author,self.total_seconds))
            print(">> Will be finished at {}".format(self.goal_time))

            self.tick.start()

        async def countdown_exists(self):
            """ Checks if the countdown message still exists """
            try:
                await self.message.channel.fetch_message(self.message.id)
                return True
            except:
                log(">> Couldn't find countdown message, assuming it doesn't exist...", True, type="warning")
                return False

        async def update_clock_display(self):
            """ Edits the countdown message with updated info """
            h = self.hour
            m = self.minute
            s = self.second

            embed = discord.Embed(colour=self.color)
            embed.add_field(name="Time left until "+self.title, value="```"+str(h).zfill(2)+":"+str(m).zfill(2)+":"+str(s).zfill(2)+"```")
            embed.set_footer(text="React with 🛑 to cancel")
            await self.message.edit(embed=embed) # edits the embed with the updates we specified above.

        async def finish(self):
            """ Called when the timer has successfully finished """
            # Send alert message
            print(">> Countdown finished")
            if self.mention_enabled:
                await self.message.channel.send("⏲️ | @here **Countdown finished, it's finally time for {}!**".format(self.title))
            else:
                await self.message.channel.send("⏲️ | **Countdown finished, it's finally time for {}!**".format(self.title))

            # Set the clock to 0
            embed = discord.Embed(colour=self.color)
            embed.add_field(name="Time left until "+self.title, value="```00:00:00```")
            embed.set_footer(text="React with 🛑 to cancel")
            await self.message.edit(embed=embed) # edits the embed with the updates we specified above.
            self.tick.cancel()

        async def stop(self):
            """ Forces the countdown to stop """
            await self.message.delete()
            await self.message.channel.send("⏲️ | **The countdown has been canceled!**")

        def update_times(self):
            """ Updates the current time remaining """
            self.hour = self.total_seconds//3600
            self.minute = (self.total_seconds%3600)//60
            self.second = (self.total_seconds%3600)%60

        @tasks.loop(seconds=1.0)
        async def tick(self):
            """ Checks the status of the timer each second """
            now = datetime.datetime.now()
            goal = self.goal_time
            self.total_seconds = int((goal - now).total_seconds())
            self.update_times()

            if (self.total_seconds <= 0) or (self.goal_time <= now):
                await self.finish()
            elif not await self.countdown_exists():
                self.tick.cancel()
                print(">> Countdown has been canceled")
            else:
                await self.update_clock_display()



    @commands.command(pass_context=True)
    @commands.guild_only()
    async def countdown(self, ctx, title, time=None, hexcode="#23272A", m=None):
        """ Creates a countdown inside an embedded message. """
        bot = self.bot
        channel = ctx.message.channel

        if hexcode == "-m": # In case someone doesn't put in a color but wants to be mentioned
                m = "-m"
                hexcode = "#23272A"

        color = '0x' + hexcode.strip('#') # Converts the hexcode to a format that our code can read (0x23272A)

        if ctx.message.guild.id in self.timers: # If a timer is already running
            await bot.send_message(channel,"❌ | **There's already a timer running! Try to cancel it first.**")

        elif time==None: # If someone puts down an invalid time.
            print(">> A countdown command was executed, but failed due to invalid arguments.")
            await bot.send_message(channel,"❌ | **Invalid Syntax. Proper usage:** `c|countdown \"title\" HH:MM:SS #000000 -m` **(-m: mention** `@everyone` **when complete, omit to disable)**")

        else:
            hh = time[0:2] # Breaks up parts of the command into integers we can use
            mm = time[3:5]
            ss = time[6:]

            mention = True if m == '-m' else False

            if int(ss) > 59 or int(mm) > 59 or int(hh) > 99: # Time is capped at 99:59:59, gotta also make sure we're using 60 second and minute intervals
                await bot.send_message(channel,"❌ | **Invalid Time!**")
                return

            # Initial setup of the embedded message begins here
            embed = discord.Embed(colour=int(color,16))
            embed.add_field(name="Time left until "+title, value="```"+hh+":"+mm+":"+ss+"```")
            embed.set_footer(text="React with 🛑 to cancel")
            msg = await channel.send(embed=embed)
            await msg.add_reaction('🛑')

            self.timers[ctx.message.guild.id] = self.CountdownClock(msg, title, hh, mm, ss, int(color,16), mention) # Stores the message for later
            await ctx.message.delete()

            # Wait for someone to cancel the timer
            def check(reaction, user):
                return (user == ctx.message.author or user.id == self.bot.ownerID) and (str(reaction.emoji) == '🛑' and reaction.message.id == msg.id)

            try:
                await bot.wait_for('reaction_add',check=check, timeout=self.timers[ctx.message.guild.id].total_seconds+1)
                await self.timers[ctx.message.guild.id].stop()
                self.timers.pop(ctx.message.guild.id) # deletes the stored clock data
                print(">> {}'s timer has been canceled.".format(ctx.message.author))
            except asyncio.TimeoutError:
                self.timers.pop(ctx.message.guild.id) # deletes the stored clock data
                #await asyncio.sleep(3)
                #msg.delete()

    @countdown.error
    async def countdown_on_error(self, ctx, error):
        log(">> {} executed a failed countdown: {}".format(ctx.message.author,error), True, type="error")
        log(type="trace")
        await self.bot.send_message(ctx.message.channel,"❌ | **Invalid Syntax. Proper usage:** `c|countdown \"title\" HH:MM:SS #000000 -m` **(-m: mention `@everyone` when complete, omit to disable)**")



    # Invite Cards
    @commands.command(pass_context=True)
    @commands.guild_only()
    async def invite(self, ctx, title, desc, limit=None, img_url=None, hexcode="#23272A"):
        """
        Creates an invite card for a specified event.
        Members of the server then can RSVP for the event by leaving a reaction on the bot's  message.

        The bot also gives the event organizer a few options as well (not yet implemented):
        - Request IDs of members who've accepted the invite (for mentioning)
        - Directly notify members via DMs
        - Cancel/Close the invite
        """
        bot = self.bot

        print(">> Creating an invite card for {}: {}".format(ctx.message.author,title))
        color = '0x' + hexcode.strip('#') # Converts the hexcode to a format that our code can read (0x23272A)

        # Setting default image if one is requested
        #if img_url.lower() == "default":
        #    img_url = generate_banner(hexcode)
        #    TODO: Find a way to return a url for generated banner images.


        # Initial setup of the embedded message begins here
        await bot.send_typing(ctx.message.channel)
        try:
            embed = discord.Embed(colour=int(color,16))
            embed.set_image(url=img_url)
        except ValueError:
            embed = discord.Embed(colour=0x23272A)
            print(">> Value Error occured with color value, setting to default...")
        except discord.HTTPException:
            #embed.set_image(url=img_url)generate_banner("0x23272A")
            print(">> HTTP Exception occured trying to set embed image, using default...")

        embed.set_footer(text="REACT WITH \"✅\" TO ACCEPT THIS INVITE")
        embed.add_field(name="**"+title+"**", value=desc+"\n\n**Event Organizer**: "+ctx.message.author.name+"\n**Limit**: "+str(limit))

        invite_card = await ctx.message.channel.send(embed=embed)
        await ctx.message.delete()

        # Add reactions that'll serve as buttons
        options = ['✅'] #, '📇', '💬', '❌']
        for reaction in options:
            await invite_card.add_reaction(reaction)


        # DM descriptions of each option to event organizer
        #await bot.send_message(ctx.message.author, "```Event Organizer Options```\nReact to the invite message to trigger the following options:\n📇:  *Have me DM you a list of users who have accepted your invite, it'll be in a format where you can copy and paste it as a message that will mention all those users.*\n💬: *Have me send a custom DM to all the members who've accepted the invite.*\n❌: *Close the invite.*\n``` ```")

        # TODO: Implement invite options

        # Remove bot's reaction once someone leaves their own
        def check(reaction, user):
            return (user != bot.user) and (str(reaction.emoji) == '✅' and reaction.message.id == invite_card.id)
        await bot.wait_for('reaction_add',check=check)
        await invite_card.remove_reaction('✅',bot.user)

    @invite.error
    async def invite_on_error(self, ctx, error):
        log(">> An invite command was executed by {}, but it failed: {}".format(ctx.message.author,error), True, type="error")
        log(type="trace")
        await self.bot.send_message(ctx.message.channel,"❌ | **Invalid Syntax. Proper usage:** `c|invite \"title\" \"description\" user_limit bannerImg_url #000000` **(Title & Description are required, type \"None\" for all other variables you would like to exclude)**")




def setup(bot):
    bot.add_cog(Utility(bot))
