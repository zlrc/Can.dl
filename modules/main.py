# Maintenance Commands
import discord
from discord.ext import commands
from wax.logger import log
import ast

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *categories):
        """ A command to reload Cogs / Modules """
        if not categories:
            await self.bot.send_message(ctx.message.channel,"❌ | **Syntax error, please list a module!**")
        else:
            success = "" # tracking successful reloads
            for cog in categories:
                try:
                    self.bot.reload_cog(cog)
                    success += "`" + cog + "` "
                except commands.errors.ExtensionNotLoaded:
                    log(">> Failed to reload cog: {}".format(cog), True, type="error")

            await self.bot.send_message(ctx.message.channel, "🔄 | **Reloaded the following modules: {}**".format(success))

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def refresh(self, ctx):
        """ Reloads all of the loaded modules """
        self.bot.refresh_cogs()
        await self.bot.send_message(ctx.message.channel, "🔄 | **Modules have been refreshed.**")



    async def execfn(self, ctx, fn):
        """
        Intended to be used with c|evalfn.

        If a code block is used with that command, it will run this function,
        which will convert the code block into a python function we can actually
        run and spit the results back out as a string.
        """

        fn_name = "_eval_expr" # we're gonna recreate a function you normally see here, so it needs a name.

        # Split each new line into seperate strings, add indentation, then join them back together.
        cmd = fn.strip("`")
        inp = "\n".join(f"    {i}" for i in cmd.splitlines())
        print(">>> EVAL: {}".format(inp))

        # Now we need to wrap our code in an async function
        body = (f"async def {fn_name}():\n" + inp)

        parsed = ast.parse(body) # parsing the codeblock so that it's readable(?)
        body = parsed.body[0].body

        # If we get an expression at the end (e.g. 'x+2'), then make it a return statement
        if isinstance(body[-1], ast.Expr): # negative list index goes from the right instead of left
            body[-1] = ast.Return(body[-1].value)

        ast.fix_missing_locations(body[-1])

        # Need to re-declare variables that discord.py uses, since this is a fresh python script
        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            'import': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        await self.bot.send_typing(ctx.message.channel) # used to indicate the command went through
        return (await eval(f"{fn_name}()", env))

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def evalfn(self, ctx, *, arg):
        """
        [Debug Command]
        Runs python script directly from Discord
        """
        if ctx.message.author.id == self.bot.ownerID: # to be extra safe
            msg = ctx.message.content.lstrip('c|evalfn')

            try: # we're gonna see if eval() can run without a problem, otherwise use exec()
                await self.bot.send_message(ctx.message.channel, "```python\n>>> {} \n{}```".format(msg, eval(arg)))
                print(">> EVAL: {}".format(msg))
            except SyntaxError:
                await self.execfn(ctx, arg)
        else:
            print(">> {} attempted to use eval command, but failed.".format(ctx.message.author))



    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """ Shuts the bot down """
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.send_message(ctx.message.channel, "🌬️🕯️")
        log(">> Bot Shutdown Executed", True, type="warning")

        await self.bot.close()



    @reload.error
    @refresh.error
    @evalfn.error
    async def on_maintenance_error(self, ctx, error):
        log(error, True, type="error")
        await self.bot.send_message(ctx.message.channel,"❌ | **Error! Please check the console.**")


def setup(bot):
    bot.add_cog(Maintenance(bot))
