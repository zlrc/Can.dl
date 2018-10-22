# Admin Commands
import discord
from discord.ext import commands
from builtins import bot
import asyncio
import ast
import json

@bot.command(pass_context=True)
async def cherrypick(ctx, keyword, amount=10):
    """
    Selectively purges messages containing a specific keyword.

    If the keyword is an @ mention of a user, it'll delete messages
    made by the mentioned user.
    """

    if ctx.message.author.server_permissions.administrator: # person using this command is an admin

        char = [str(s) for s in keyword] # break up message into a list of individual characters.

        if ('@' and '<' and '>') in char: # detects if a mention is used
            await bot.send_typing(ctx.message.channel)

            # Delete messages where author id matches mentioned user's id, but isn't the original message.
            def usr(m):
                return m.author.id == ctx.message.mentions[0].id

            await bot.delete_message(ctx.message)
            deleted = await bot.purge_from(ctx.message.channel, limit=amount, check=usr)
            status = await bot.send_message(ctx.message.channel, "🍒 | **{} messages have been successfully deleted.**".format(len(deleted)))

            mentionee = str(ctx.message.mentions[0]) + "'s" # commas in the print function add spaces by default, this bypasses that.
            print(">>",ctx.message.author,"deleted",len(deleted),"of",mentionee,"messages.")

            await asyncio.sleep(5)
            await bot.delete_message(status)

        else:
            await bot.send_typing(ctx.message.channel)

            # Delete messages where the keyword is found
            def key(m):
                return keyword in m.content

            await bot.delete_message(ctx.message)
            deleted = await bot.purge_from(ctx.message.channel, limit=amount, check=key)
            status = await bot.send_message(ctx.message.channel, "🍒 | **{} messages have been successfully deleted.**".format(len(deleted)))
            print(">>",ctx.message.author,"deleted",len(deleted),"messages containing the keyword:",keyword)

            await asyncio.sleep(5)
            await bot.delete_message(status)

    else:
        await bot.send_message(ctx.message.channel, "❌ | **You do not have permission to use that command!**")

@cherrypick.error
async def cherrypick(error, ctx):
    print(">> A cherrypick command was executed, but it failed...")
    print(error)
    await bot.send_message(ctx.message.channel,"❌ | **Invalid Syntax. Proper usage:** `c|cherrypick keyword search_limit`")



async def execfn(ctx, fn):
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
    print(">>> EVAL:",inp)

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

    await bot.send_typing(ctx.message.channel) # used to indicate the command went through
    return (await eval(f"{fn_name}()", env))

@bot.command(pass_context=True, hidden=True)
async def evalfn(ctx, *, arg):
    """
    [Debug Command]
    Runs python script directly from Discord
    """
    with open("config.json") as cfg:
        config = json.load(cfg)

    if ctx.message.author.id == config["ownerID"]:
        msg = ctx.message.content.lstrip('c|evalfn')

        try: # we're gonna see if eval() can run without a problem, otherwise use exec()
            await bot.send_message(ctx.message.channel, "```python\n>>> {} \n{}```".format(msg, eval(arg)))
            print(">> EVAL:",msg)
        except SyntaxError:
            await execfn(ctx, arg)
    else:
        print(">>",ctx.message.author,"attempted to use eval command, but failed.")

@evalfn.error
async def evalfn_on_error(error, ctx):
    print(error)
    await bot.send_message(ctx.message.channel,"❌ | **Error! Please check the console.**")



@bot.command(pass_context=True)
async def napalm(ctx):
    """ Simulates a napalm by spamming fire emojis then deleting a bunch of messages. """

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
                print ('>>',ctx.message.author,'activated command: \"c|napalm\"')
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



@bot.command(pass_context=True, hidden=True)
async def shutdown(ctx):
    """
    [Debug Command]
    Shuts the bot down
    """
    with open("config.json") as cfg:
        config = json.load(cfg)

    if ctx.message.author.id == config["ownerID"]:
        await bot.send_typing(ctx.message.channel)
        await bot.send_message(ctx.message.channel, "🌬️🕯️")
        print(">> Bot Shutdown Executed")

        await bot.close()
    else:
        print(">>",ctx.message.author,"attempted to shut the bot down, but failed.")
