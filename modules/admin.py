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




def setup(bot):
    bot.add_cog(Admin(bot))
