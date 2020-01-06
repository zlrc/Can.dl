# "Fun" Commands, typically generators and search queries
import discord
from discord.ext import commands
import aiohttp
from asyncio import TimeoutError
import requests
import random
from bs4 import BeautifulSoup
import markovify
import os
import wax.helpers as h_
from wax.logger import log

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.madlib_running = {}

    # Mad Libs
    def get_lib_template(self):
        """ Returns a random lib from the db/madlibs folder """
        rand_file = "db/madlibs/" + random.choice(os.listdir("db/madlibs"))
        with open(rand_file,"r") as file:
            # Returns the title of the lib, number of blanks, and the story itself.
            title = file.readline().strip('\n')
            blanks = file.readline().strip('\n')
            text = file.readline()
            return title, blanks, text

    async def get_lib_input(self, channel, wclass, index, total):
        """ Asks users for the given word class and returns the first response it gets """
        bot = self.bot

        await bot.send_message(channel,"📜 | **[{}/{}] Please give me a** ***{}***".format(index, total, wclass))

        def is_valid(m):
            return ((m.author != bot.user) and (not (m.attachments or 'c|' in m.clean_content))) and m.channel == channel

        try:
            input = await bot.wait_for('message', check=is_valid, timeout=300)
            return input.clean_content # .partition(' ')[0] to grab the first word only
        except TimeoutError:
            return '> CANCEL'

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def madlib(self, ctx):
        """ Walks you through a fill-in-the blank story. """
        bot = self.bot

        if ctx.message.guild.id in self.madlib_running:
            await bot.send_message(ctx.message.channel, "❌ | **There's already a story in progress! Type** `> CANCEL` **to end it.**")
            return

        self.madlib_running[ctx.message.guild.id] = True
        await bot.send_message(ctx.message.channel,"```A lib has started!\nType \"> CANCEL\" to stop.```")
        title, total_blanks, template_string = self.get_lib_template()
        new_string = ""
        progress = 0

        # Loop through each word, replace the ones with spoiler tags
        for index, word in enumerate(template_string.split('_')):
            if (word[0:2] == '||'): # if the word has spoiler tags
                progress += 1

                input_string = await self.get_lib_input(ctx.message.channel, word.strip('|'), progress, total_blanks)

                if (input_string == '> CANCEL'):
                    await bot.send_message(ctx.message.channel,"📜 | **Canceled! Here is what you had up to this point:**")
                    break

                new_string += "||" + input_string + "||"
            else:
                new_string += word

        await bot.send_message(ctx.message.channel,"```{}```{}```-- END --```".format(title,new_string))
        self.madlib_running.pop(ctx.message.guild.id)

    @madlib.error
    async def madlib_error(self, ctx, error):
        log(">> {} attempted to run c|madlib, but failed: {}".format(ctx.message.author,error), True, type="error")
        log(type="trace")



    # Markov Chains
    def tomarkov(self, string):
        """ Returns a randomly generated sentence from the string provided """

        # Generate a random state size between 2 and 4
        #states = random.randint(2,4)

        # Build the model
        string_model = markovify.NewlineText(string, retain_original=True, state_size=2)

        # Construct the requested sentence(s)
        markov_string = ""
        for i in range(random.randint(1,5)): # 1 to 5 sentences are strung together
            markov_string += str(string_model.make_sentence(tries=100)) + "\n"

        # Return the final string
        if "None" in markov_string:
            return "❌ | **Error! Failed to generate markov chain, post some more before trying again.**"
        else:
            return markov_string;

    async def markovuser(self, message, member, target_channel):
        """ Runs when c|markov is targeted to a particular user """
        bot = self.bot

        async with message.channel.typing():
            log = target_channel.history(limit=5000) # grabs last n messages

            # Put all of the valid messages together as a single string
            string = ""
            async for i in log: # for every message in the log
                if (i.author.id == member.id) and (not "c|" in i.clean_content):
                    string += i.clean_content + "\n"

            # Generate chain from messages, keep trying if there's an error
            msg = self.tomarkov(string)
            attempts = 1
            while ("❌ |" in msg) and (attempts <= 5):
                print("    >> Failed, trying again... ({}/5)".format(attempts) )
                log = target_channel.history(limit=5000+(1000*attempts))
                #start = 5000 + ( 1000*(attempts-1) )

                string = ""
                async for i in log:
                    if (i.author.id == member.id) and (not "c|" in i.clean_content):
                        string += i.clean_content + "\n"
                msg = self.tomarkov(string)
                attempts += 1


            # Create an embed to simulate a user quote
            embed = discord.Embed(color=member.color, description=msg)
            embed.set_author(name=member.display_name, icon_url=member.avatar_url)

            # Send results
            await bot.send_message(message.channel,embed=embed)

    async def markovchannel(self, message, target_channel):
        """ Runs when c|markov is targeted to a particular channel """
        bot = self.bot

        async with message.channel.typing():
            log = target_channel.history(limit=1000) # grabs last n messages
            
            # Put all of the valid messages together as a single string
            string = ""
            async for i in log: # for every message in the log
                if (i.author != bot.user) and (not "c|" in i.clean_content):
                    string += i.clean_content + "\n"

            # Send results
            await bot.send_message(message.channel, self.tomarkov(string) )

    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(2,20, commands.BucketType.channel)
    async def markov(self, ctx, user=None, chan=None):
        """ Generates a Markov Chain from recent messages. """
        bot = self.bot

        print(">> {} requested a markov chain, processing...".format(ctx.message.author)) # log command usage

        # Convert channel to an object we can work with
        if chan: # sets default channel if one isn't provided
            chan = ctx.message.guild.get_channel(int(chan[2:-1]))
        else:
            chan = ctx.message.channel


        def user_is(type, u): # bypasses TypeError exception when user=None
            if type == "channel":
                try:
                    if ctx.message.guild.get_channel(int(u[2:-1])):
                        return True
                    else:
                        return False
                except TypeError:
                    return False
            elif type == "member":
                try:
                    if ctx.message.guild.get_member_named(user):
                        return True
                    else:
                        return False
                except TypeError:
                    return False

        # Compile a string of messages that meet the criteria
        if ctx.message.mentions: # checks if a mention was used
            await self.markovuser(ctx.message, ctx.message.mentions[0], chan)
        elif user_is("member", user): # if mention wasn't used to find user
            await self.markovuser(ctx.message, ctx.message.guild.get_member_named(user), chan)
        elif user_is("channel", user): # if a channel was given without user mention
            await self.markovchannel(ctx.message, ctx.message.guild.get_channel(int(user[2:-1])))
        else:
            async with ctx.message.channel.typing():
                log = ctx.message.channel.history(limit=800) # grabs last n messages

                # Put all of the valid messages together as a single string
                string = ""
                async for i in log: # for every message in the log
                    if (i.author != bot.user) and (not "c|" in i.clean_content):
                        string += i.clean_content + "\n"

                # Send results
                await bot.send_message(ctx.message.channel, self.tomarkov(string) )

    @markov.error
    async def markov_error(self, ctx, error):
        log(">> {} attempted to run c|markov, but failed: {}".format(ctx.message.author,error), True, type="error")
        if isinstance(error, commands.CommandOnCooldown):
            await self.bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            log(type="trace")
            await self.bot.send_message(ctx.message.channel,"❌ | **Error! Proper Syntax:** `c|markov @user #channel` **(user and channel optional)**")



    # Stack Overflow Lookup
    @commands.command(pass_context=True)
    @commands.guild_only()
    async def stack(self, ctx, *,args):
        """ Searches Stack Overflow and returns the top result. """
        search_url = requests.get("https://stackoverflow.com/search?q=" + h_.convert_to_url(args))
        soup = BeautifulSoup(search_url.content, "html.parser")
        await self.bot.send_typing(ctx.message.channel)

        # Find the first <a> element that has the URL we need, convert to a url.
        top_result = soup.find('a', {'class': "question-hyperlink"})
        result_url = "https://stackoverflow.com" + top_result.get('href')

        await self.bot.send_message(ctx.message.channel, "{}".format(result_url))

    @stack.error
    async def stack_error(self, ctx, error):
        log(">> c|stack: {}".format(error), type="error")
        await self.bot.send_message(ctx.message.channel,"❌ | **Please enter a valid search query!**")



    # TV Tropes
    @commands.command(pass_context=True)
    @commands.guild_only()
    async def trope(self, ctx, *,args=None):
        """ Returns a random tv tropes page. """
        bot = self.bot
        await bot.send_typing(ctx.message.channel)

        if not args:

            # Opens up a random page through a special url, saves it as the variable: "url"
            async with aiohttp.ClientSession() as sess:
                async with sess.get("http://tvtropes.org/pmwiki/randomitem.php?p="+str(random.randint(1,9999999999))) as url:
                    await bot.send_message(ctx.message.channel, "{}".format(url.url))





def setup(bot):
    bot.add_cog(Fun(bot))
