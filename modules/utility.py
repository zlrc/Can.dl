# Utility Commands, most come with special configurations and run in the background
import discord
from discord.ext import commands
from builtins import bot
import asyncio
import os.path

async def update_ctdwn(ctx,msg,title,hh,mm,ss,color,mention):
    """
    Once a countdown has been initiated, an instance of this runs in the background.
    This is basically what makes the bot edit the countdown message every second.
    """
    h = int(hh)
    m = int(mm)
    s = int(ss)
    i = s+(60*m)+(60*60*h) # Total time left in seconds.
    print(">>",ctx.message.author,"created a timer for:",i,"seconds.")

    if os.path.isfile("countdown_cache.py"): # Checks if a cache file exists
        while i >= 0 and os.path.isfile("countdown_cache.py"): # As long as we have time remaining and the message hasn't been deleted.
            if s > 0:
                s -= 1
            elif m > 0: # If we're out of seconds, then see if we can subtract minutes.
                m -= 1
                s = 59
            elif h > 0: # Once we're out of minutes, try subtracting hours.
                h -= 1
                m = 59
                s = 59
            elif i == 0:
                os.remove("countdown_cache.py")
                if mention == "-m":
                    await bot.send_message(ctx.message.channel,"⏲️ | @everyone **Countdown finished, it's finally time for {}!**".format(title))
                else:
                    await bot.send_message(ctx.message.channel,"⏲️ | **Countdown finished, it's finally time for {}!**".format(title))

            i -= 1 # After the numbers we see have been deducted appropriately, we subtract our total time left.

            try:
                # Now we create the edited countdown embed. zfill(2) adds a zero in front of numbers e.g. "5" becomes "05"
                embed = discord.Embed(colour=color)
                embed.add_field(name="Time left until "+title, value="```"+str(h).zfill(2)+":"+str(m).zfill(2)+":"+str(s).zfill(2)+"```")
                embed.set_footer(text="type \"c|countdown cancel\" to stop the countdown")
                await bot.edit_message(msg, embed=embed) # Edits the embed with the updates we specified above.

                await asyncio.sleep(1) # Wait one second before repeating the entire function again.
            except:
                print(">> Couldn't find original countdown message, cancelling command...")
                try:
                    os.remove("countdown_cache.py") # Just in case...
                except FileNotFoundError:
                    pass
                finally:
                    await asyncio.sleep(600)
                    return


@bot.command(pass_context=True)
async def countdown(ctx, title, time=None, hexcode="#23272A", m=None):
    """ Creates a countdown inside an embedded message. """

    channel = ctx.message.channel
    if hexcode == "-m": # In case someone doesn't put in a color but wants to be mentioned
            m = "-m"
            hexcode = "#23272A"

    color = '0x' + hexcode.strip('#') # Converts the hexcode to a format that our code can read (0x23272A)
    data = [ctx.message.author.id,ctx.message.channel.id] # Saving who made the countdown and in which channel.

    if title == "cancel" and time == None: # Cancelling the countdown
        if os.path.isfile("countdown_cache.py"):
            from countdown_cache import data

            if (data[0] == ctx.message.author.id) or (ctx.message.author.server_permissions.manage_messages): # Must be countdown creator or an admin
                def findcountdown(m): # Compares message IDs with what we have saved in countdown_cache.py
                    return m.id == data[2]

                await bot.purge_from(ctx.message.channel, limit=500, check=findcountdown)
                await bot.delete_message(ctx.message)

                await bot.send_message(ctx.message.channel,"⏲️ | **The countdown has been canceled!**")
                print(">>",ctx.message.author,"canceled the timer.")
                os.remove("countdown_cache.py")
            else:
                await bot.send_message(channel,"❌ | **That isn't your timer! Please ask the creator of that timer or an admin to cancel it for you.**")
        else:
            await bot.send_message(channel,"❌ | **There isn't even a timer running!**")
    elif os.path.isfile("countdown_cache.py"): # If the file exists....
        await bot.send_message(channel,"❌ | **There's already a timer running! Cancel it first by typing `c|countdown cancel`**")
    elif title != "cancel" and time==None: # If someone puts down an invalid time.
        print(">> A countdown command was executed, but it failed...")
        print("time is a required argument that is missing.")
        await bot.send_message(channel,"❌ | **Invalid Syntax. Proper usage:** `c|countdown \"title\" HH:MM:SS #000000 -m` **(-m: mention** `@everyone` **when complete, omit to disable)**")
    else:
        hh = time[0:2] # Breaks up parts of the command into integers we can use
        mm = time[3:5]
        ss = time[6:]

        if int(ss) > 60 or int(mm) > 60 or int(hh) > 99: # Time is capped at 99:99:99, gotta also make sure we're using 60 second and minute intervals
            await bot.send_message(channel,"❌ | **Invalid Time!**")
            return

        # Initial setup of the embedded message begins here
        embed = discord.Embed(colour=int(color,16))
        embed.add_field(name="Time left until "+title, value="```"+hh+":"+mm+":"+ss+"```")
        embed.set_footer(text="type \"c|countdown cancel\" to stop the countdown")
        msg = await bot.send_message(channel, embed=embed)

        data.append(msg.id) # Stores the message we just sent so we can access it later.
        f = open("countdown_cache.py","w+")
        f.write("data = " + str(data))
        f.close()

        bot.loop.create_task(update_ctdwn(ctx,msg,title,hh,mm,ss,int(color,16),m)) #Creates message as a background task that updates

@countdown.error
async def countdown_on_error(error, ctx):
    print(">> A countdown command was executed, but it failed...")
    print(error)
    await bot.send_message(ctx.message.channel,"❌ | **Invalid Syntax. Proper usage:** `c|countdown \"title\" HH:MM:SS #000000 -m` **(-m: mention `@everyone` when complete, omit to disable)**")


@bot.command(pass_context=True)
async def invite(ctx, title, desc, limit=None, img_url=None, hexcode="#23272A"):
    """
    Creates an invite card for a specified event.
    Members of the server then can RSVP for the event by leaving a reaction on the bot's  message.

    The bot also gives the event organizer a few options as well (not yet implemented):
    - Request IDs of members who've accepted the invite (for mentioning)
    - Directly notify members via DMs
    - Cancel/Close the invite
    """

    print(">> Creating an invite card for",ctx.message.author,":",title)
    color = '0x' + hexcode.strip('#') # Converts the hexcode to a format that our code can read (0x23272A)

    # Setting default image if one is requested
    #if img_url.lower() == "default":
    #    img_url = generate_banner(color)
    #    todo: Find a way to return a url for generated banner images.


    # Initial setup of the embedded message begins here
    await bot.send_typing(ctx.message.channel)
    try:
        embed = discord.Embed(colour=int(color,16))
        embed.set_image(url=img_url)
    except ValueError:
        embed = discord.Embed(colour=0x23272A)
        print(">> Value Error occured with color value, setting to default...")
    except HTTPException:
        #embed.set_image(url=img_url)generate_banner("0x23272A")
        print(">> HTTP Exception occured trying to set embed image, using default...")

    embed.set_footer(text="REACT WITH \"✅\" TO ACCEPT THIS INVITE")
    embed.add_field(name="**"+title+"**", value=desc+"\n\n**Event Organizer**: "+ctx.message.author.name+"\n**Limit**: "+str(limit))

    invite_card = await bot.send_message(ctx.message.channel, embed=embed)
    await bot.delete_message(ctx.message)

    # Add reactions that'll serve as buttons
    options = ['✅'] #, '📇', '💬', '❌']
    for reaction in options:
        await bot.add_reaction(invite_card,reaction)


    # DM descriptions of each option to event organizer
    #await bot.send_message(ctx.message.author, "```Event Organizer Options```\nReact to the invite message to trigger the following options:\n📇:  *Have me DM you a list of users who have accepted your invite, it'll be in a format where you can copy and paste it as a message that will mention all those users.*\n💬: *Have me send a custom DM to all the members who've accepted the invite.*\n❌: *Close the invite.*\n``` ```")

    # todo: Implement invite options

@invite.error
async def invite_on_error(error, ctx):
    print(">> An invite command was executed, but it failed...")
    print(error)
    await bot.send_message(ctx.message.channel,"❌ | **Invalid Syntax. Proper usage:** `c|invite \"title\" \"description\" user_limit bannerImg_url #000000` **(Title & Description are required, type \"None\" for all other variables you would like to exclude)**")
