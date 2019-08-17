# Admin Commands
from discord.ext import commands
from wax.logger import log

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cherrypick(self, ctx, mode, amount=10, *keywords):
        """
        Selectively purges messages containing specific keywords.

        If the mode is an @ mention of a user, it'll delete messages
        made by the mentioned user.
        """
        bot = self.bot
        channel = ctx.message.channel

        # Different checks for each mode
        def all_check(m):
            for keyword in keywords:
                if not (keyword in m.content):
                    return False
            return True

        def any_check(m):
            for keyword in keywords:
                if keyword in m.content:
                    return True

        def usr_check(m):
            if m.author.id == ctx.message.mentions[0].id and len(keywords) > 0:
                for keyword in keywords:
                    if keyword in m.content:
                        return True
            else:
                return m.author.id == ctx.message.mentions[0].id # no keywords given

        await bot.send_typing(channel)

        # Delete messages depending on user's preferences
        if mode == 'all': # message must have all the keywords
            await ctx.message.delete()
            deleted = await channel.purge(limit=amount, check=all_check)
            log(">> {} deleted {} messages with all these keywords: {}".format(ctx.message.author,len(deleted),keywords), True)

        elif mode == 'any': # message must have any of the keywords
            await ctx.message.delete()
            deleted = await channel.purge(limit=amount, check=any_check)
            log(">> {} deleted {} messages containing the keyword(s): {}".format(ctx.message.author,len(deleted),keywords), True)

        elif ctx.message.mentions and str(mode)[0:2] == '<@': # has to be by a certain user
            await ctx.message.delete()
            deleted = await channel.purge(limit=amount, check=usr_check)
            mentionee = ctx.message.mentions[0]
            log(">> {} deleted {} of {}#{}\'s messages.".format(ctx.message.author, len(deleted), mentionee.name, mentionee.discriminator), True)

        status = await channel.send("🍒 | **{} messages have been successfully deleted.**".format(len(deleted)))
        await status.delete(delay=5)

    @cherrypick.error
    async def cherrypick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.bot.send_message(ctx.message.channel, "❌ | **You do not have permission to use that command!**")
        else:
            log(">> {} failed to execute c|cherrypick: {}".format(ctx.message.author,error), True, type="error")
            await self.bot.send_message(ctx.message.channel,"❌ | **Invalid Syntax. Proper usage:** `c|cherrypick keyword_mode message_limit keyword(s)`")


'''
    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def napalm(self, ctx):
        """ Burns through (deletes) ~2000 messages in a fiery napalm. """
        bot = self.bot
        channel = ctx.message.channel

        # Check for permissions first
        if ctx.message.author.server_permissions.administrator: # Person using this command is an admin
            await bot.send_message(channel, "⚠️ | **Warning! Are you sure you want to napalm this channel? It will delete A LOT of messages on here, type** `yes` **or** `cancel` **to proceed.**")
            msg = await bot.wait_for_message(author=ctx.message.author,channel=channel)

            # Confirmation 1
            if msg.clean_content.lower() == "yes": # clean_content.lower() converts everything to lowercase
                await bot.send_message(channel, "⚠️ | **Are you REAAAALLLLY sure? \nType the following launch code EXACTLY to confirm:** `FortunateSon55`")
                msg2 = await bot.wait_for_message(author=ctx.message.author,channel=channel)

                # Confirmation 2
                if msg2.clean_content == "FortunateSon55":
                    print (">> {} activated c|napalm".format(ctx.message.author))
                    await bot.send_message(channel, "💣 | **Firing the napalms...**")

                    # Fire ahoy
                    await bot.send_typing(channel)
                    for i in range(5): # sends 5 messages in a row
                        napalmstr = ""
                        for i in range(2000): # each message has 2000 flame emojis
                            napalmstr += "🔥"
                        await bot.send_message(ctx.message.channel, napalmstr)

                    i = 1975
                    while i > 0:
                        await bot.purge_from(ctx.message.channel, limit=395)
                        i -= 395

                    await asyncio.sleep(5)
                    await bot.send_message(channel, "💀 | **Press F to pay respects.**")

                else:
                    await bot.send_message(channel, "❌ | **Failed to input correct launch code, ceasing operations...**")
                    return
            elif msg.clean_content.lower() == "cancel":
                await bot.send_message(channel, "**Canceled!**")
                return
            else:
                await bot.send_message(channel, "❌ | **That is not a valid response! Please re-enter the command and try again.**")
                return
        else:
            await bot.send_message(channel, "❌ | **You do not have permission to use that command!**")
'''



def setup(bot):
    bot.add_cog(Admin(bot))
