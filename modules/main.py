# Generic bot commands (mostly)
import discord
from discord.ext import commands
from builtins import bot
import random
import os.path
import sqlite3
from sqlite3 import Error
bot.remove_command('help') # Removes existing help command so that I can replace it with a fancier one

# Setting up server groups database
conn = sqlite3.connect(os.path.realpath('./db/groups.db'))


async def addgroup(ctx, x):
    if ctx.message.author.server_permissions.manage_roles and ctx.message.author.server_permissions.ban_members:
        await bot.send_typing(ctx.message.channel)
        roles = list(ctx.message.server.roles)
        s = ""

        # Turning the list of roles into a working string, or else the bot just spits out the object ids
        for i in roles[1:]:
            s += str(roles.index(i)) + ": " + str(i) + "\n"
        rolelist = await bot.send_message(ctx.message.channel,"```{}```\n🗒️ | **Type the number of the role you would like to make into a group, seperate numbers with a comma if converting multiple roles into groups. Otherwise, type **`cancel`** to quit.**".format(s))

        msg = await bot.wait_for_message(author=ctx.message.author,channel=ctx.message.channel)

        # Checks user response, then saves groups to database if valid.
        if msg.clean_content.lower() == "cancel":
            await bot.send_message(ctx.message.channel, "**Canceled!**")
            await bot.delete_message(rolelist)
            return
        else:
            try:
                nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                print(">> {} created new group(s):".format(ctx.message.author))

                # Using index numbers, we'll save information on selected roles to our database
                conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
                c = conn.cursor()

                for n in nums:
                    await bot.send_typing(ctx.message.channel)
                    role_data = (ctx.message.server.name, ctx.message.server.id, roles[n].name, roles[n].id)

                    # Check if role has been added already
                    c.execute('SELECT role_id FROM active_groups WHERE role_id=?', (roles[n].id,))

                    if not c.fetchone(): # If it doesn't exist, insert the group info as a new row
                        c.execute('INSERT INTO active_groups VALUES (?,?,?,?)', role_data)
                        conn.commit()
                        print("  {}".format(roles[n]))
                    else:
                        print("  {} [ALREADY EXISTS]".format(roles[n].name))

                await bot.send_message(ctx.message.channel,"🗒️ | **Selected roles have been successfully added as groups! Type **`c|group list`** to view these roles that users can give themselves.**")
                conn.close()

            except ValueError:
                print(">> A group command was executed, but it failed...")
                await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

            finally:
                await bot.delete_message(rolelist)

    else:
        await bot.send_message(ctx.message.channel,"❌ | **Error! Must have \"Manage Roles\" and \"Ban Members\" permission in order to use this command!**")

async def removegroup(ctx, x):
    if ctx.message.author.server_permissions.manage_roles and ctx.message.author.server_permissions.ban_members:
        conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
        c = conn.cursor()

        s = ""
        i = 1

        grouplist = [None]

        # Gather all the available role IDs into the list above
        for row in c.execute('SELECT role_id FROM active_groups WHERE server_id=?', (ctx.message.server.id,)):
            grouplist.append(int(str(row)[1:-2])) # 'row' variable shows up as '()' if not converted to a string first.
        print(">> {}".format(grouplist))

        # Compile the list of role names
        for row in c.execute('SELECT role_name FROM active_groups WHERE server_id=?', (ctx.message.server.id,)):
            role = str(row)[2:-3] # Strips the parenthesis and comma from the result

            s += str(i) + ": " + role + "\n"
            i += 1

        await bot.send_typing(ctx.message.channel)
        rolelist = await bot.send_message(ctx.message.channel,"```{}```\n🗒️ | **Type the number of the group you would like to remove, seperate numbers with a comma if removing more than one. Otherwise, type **`cancel`** to quit.**".format(s))
        msg = await bot.wait_for_message(author=ctx.message.author,channel=ctx.message.channel)

        # Checks user response, then removes groups from database if valid.
        if msg.clean_content.lower() == "cancel":
            await bot.send_message(ctx.message.channel, "**Canceled!**")
            await bot.delete_message(rolelist)
            conn.close()
        else:
            try:
                nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                print(">> {} removed groups:".format(ctx.message.author))

                for n in nums: # Deletes one row at a time
                    await bot.send_typing(ctx.message.channel)
                    c.execute('DELETE FROM active_groups WHERE role_id=?', (grouplist[n],))
                    conn.commit()
                    print("  {} | {}".format(discord.utils.get(ctx.message.server.roles, id=str(grouplist[n])),grouplist[n]))

                await bot.send_message(ctx.message.channel,"🗒️ | **Selected groups have successfully been removed! Type **`c|group list`** to view these roles that users can give themselves.**")

            except ValueError:
                print(">> A group command was executed, but it failed...")
                await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

            finally:
                await bot.delete_message(rolelist)
                conn.close()

    else:
        await bot.send_message(ctx.message.channel,"❌ | **Error! Must have \"Manage Roles\" and \"Ban Members\" permission in order to use this command!**")

async def joingroup(ctx, x):
    botperms = ctx.message.channel.permissions_for(ctx.message.server.me)

    if botperms.manage_roles:
        conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
        c = conn.cursor()

        s = ""
        i = 1

        grouplist = [None]

        # Gather all the available role IDs into the list above
        for row in c.execute('SELECT role_id FROM active_groups WHERE server_id=?', (ctx.message.server.id,)):
            grouplist.append(int(str(row)[1:-2])) # 'row' variable shows up as '()' if not converted to a string first.

        # Compile the list of role names
        for row in c.execute('SELECT role_name FROM active_groups WHERE server_id=?', (ctx.message.server.id,)):
            role = str(row)[2:-3] # Strips the parenthesis and comma from the result

            s += str(i) + ": " + role + "\n"
            i += 1

        await bot.send_typing(ctx.message.channel)
        rolelist = await bot.send_message(ctx.message.channel,"```{}```\n🗒️ | **Type the number of the group you would like to join, seperate numbers with a comma if joining more than one. Otherwise, type **`cancel`** to quit.**".format(s))
        msg = await bot.wait_for_message(author=ctx.message.author,channel=ctx.message.channel)

        # Checks user response, joins groups if valid.
        if msg.clean_content.lower() == "cancel":
            await bot.send_message(ctx.message.channel, "**Canceled!**")
            await bot.delete_message(rolelist)
            conn.close()
        else:
            try:
                nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                print(">> {} joined the following groups:".format(ctx.message.author))

                for n in nums:
                    grouprole = discord.utils.get(ctx.message.server.roles, id=str(grouplist[n])) # Finding the role by ID
                    await bot.add_roles(ctx.message.author, grouprole)
                    print("  {}".format(grouprole))

                await bot.send_message(ctx.message.channel,"🗒️ | **Successfully joined group(s)!**")

            except ValueError:
                print(">> A group command was executed, but it failed...")
                await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

            finally:
                await bot.delete_message(rolelist)
                conn.close()
    else:
        await bot.send_message(ctx.message.channel,"❌ | **Error! I do not have permission to manage roles!**")

async def leavegroup(ctx, x):
    botperms = ctx.message.channel.permissions_for(ctx.message.server.me)

    if botperms.manage_roles:
        conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
        c = conn.cursor()

        s = ""
        i = 1

        grouplist = [None]

        # Gather all the available role IDs into the list above
        for row in c.execute('SELECT role_id FROM active_groups WHERE server_id=?', (ctx.message.server.id,)):
            grouplist.append(int(str(row)[1:-2])) # 'row' variable shows up as '()' if not converted to a string first.

        # Compile the list of role names
        for row in c.execute('SELECT role_name FROM active_groups WHERE server_id=?', (ctx.message.server.id,)):
            role = str(row)[2:-3] # Strips the parenthesis and comma from the result

            s += str(i) + ": " + role + "\n"
            i += 1

        await bot.send_typing(ctx.message.channel)
        rolelist = await bot.send_message(ctx.message.channel,"```{}```\n🗒️ | **Type the number of the group you would like to leave, seperate numbers with a comma if leaving more than one. Otherwise, type **`cancel`** to quit.**".format(s))
        msg = await bot.wait_for_message(author=ctx.message.author,channel=ctx.message.channel)

        # Checks user response, leaves groups if valid.
        if msg.clean_content.lower() == "cancel":
            await bot.send_message(ctx.message.channel, "**Canceled!**")
            await bot.delete_message(rolelist)
            conn.close()
        else:
            try:
                nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                print(">> {} left the following groups:".format(ctx.message.author))

                for n in nums:
                    grouprole = discord.utils.get(ctx.message.server.roles, id=str(grouplist[n])) # Finding the role by ID
                    await bot.remove_roles(ctx.message.author, grouprole)
                    print("  {}".format(grouprole))

                await bot.send_message(ctx.message.channel,"🗒️ | **Successfully left group(s)!**")

            except ValueError:
                print(">> A group command was executed, but it failed...")
                await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

            finally:
                await bot.delete_message(rolelist)
                conn.close()
    else:
        await bot.send_message(ctx.message.channel,"❌ | **Error! I do not have permission to manage roles!**")

async def listgroups(ctx, x):
    conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
    c = conn.cursor()
    s = ""
    i = 1

    print(">> {} listed the groups!".format(ctx.message.author))
    for row in c.execute('SELECT role_name FROM active_groups WHERE server_id=?', (ctx.message.server.id,)):
        role = str(row)[2:-3] # Strips the parenthesis and comma from the result

        s += str(i) + ": " + role + "\n"
        i += 1
        print("  {}".format(role))

    await bot.send_typing(ctx.message.channel)
    await bot.send_message(ctx.message.channel,"🗒️ | **Roles that users can gives themselves (groups) are as follows:**\n```{}```".format(s))
    conn.close()

@bot.command(pass_context=True)
async def group(ctx, func):
    """
    Gives the option to turn any role of choosing into a 'group'
    that users can join to give themselves that particular role.

    This command is intended to give non-admin users the ability
    to give themselves roles that they normally would have to ask
    someone else to in order to get them (color roles, teams, etc.)

    addgroup - Adds roles to the list of groups members can join
    removegroup - Removes roles from the list of groups members can join
    joingroup - Assigns roles that user specifies
    leavegroup - Removes roles that user specifies
    """

    # Set up a table if one doesn't exist already
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE active_groups
                 (server_name text, server_id integer, role_name text, role_id integer)''')
        conn.commit()
        print(">> No groups data table found, generating a new one...")
    except:
        pass

    # Python doesn't have case switches, so we're just gonna use a dictionary instead.
    options = {
        "add": addgroup,
        "remove": removegroup,
        "join": joingroup,
        "leave": leavegroup,
        "list": listgroups
    }
    await options[func](ctx, func)

@group.error
async def group(error, ctx):
    print(">> A group command was executed, but it failed...")
    print(error)
    await bot.send_message(ctx.message.channel,"❌ | **Invalid Syntax. Proper usage:** `c|group option` **(options: **`add`**, **`remove`**, **`join`**, **`leave`**, **`list`**)**")


@bot.command(pass_context=True)
async def help(ctx):
    helpmsg = discord.Embed(color=0xe0216a, url=" ", description="All commands must start with **c|** (e.g. *c|help*).")

    helpmsg.set_author(name="🕯️ "+bot.user.name+" Commands")
    helpmsg.set_footer(text="[Page 1 of 1]")

    helpmsg.add_field(name="Default:", value="`group` - Provides options for roles that a user can assign themselves without the need of a 'Manage Roles' permission (i.e. voluntary roles like colors and whatnot). Available roles can be configured by an admin. \n`help` - Pulls up this message. \n`ping` - Responds with 'pong!', used to check response time of the bot. \n`someone` - mentions a random user with the included message. \ne.g. *\"c|someone hello there!\"* \n   ")
    helpmsg.add_field(name="Fun:", value="`markov` - Randomly generates a markov chain from messages in the chat.\n`trope` - Returns a random TV Tropes page.\n`stack` - Searches StackOverflow with the provided input.\n   ")
    helpmsg.add_field(name="Utility:", value="`countdown` - Starts a countdown timer that the bot updates in real time. Restricted to one countdown at a time since it's a little finnicky. \ne.g. *\"c|countdown title 01:30:05 #23272A -m\"* (including `-m` makes it mention everyone once finished)\n`invite` - Creates a fancy embedded invite card for people to react to as a way to RSVP for an upcoming event. For syntax information, trigger the command without any arguments (i.e. just type \"c|invite\").\n    ")
    helpmsg.add_field(name="Admin:", value="`cherrypick` - Purges a given number of messages that meet the provided criteria, which can be either a user or keyword.\ne.g *\"c|cherrypick lasagna 25\"* (the number is how many messages to ***check*** the keyword for, not how many you want to delete) \n`napalm` - Purges 1975 messages in the channel with a fiery napalm. Prompts with a warning before use. \n    ")

    await bot.send_message(ctx.message.author, embed=helpmsg)


@bot.command(pass_context=True)
async def ping(ctx):
    print(">> pong!")
    channel = ctx.message.channel
    await bot.send_typing(ctx.message.channel)

    await bot.send_message(channel, "pong!")


@bot.command(pass_context=True)
@commands.cooldown(1,8, commands.BucketType.channel)
async def someone(ctx):
    channel = ctx.message.channel
    users = list(ctx.message.server.members) # Grabs a dictionary of users on the server, then converts it to a list
    msg = ctx.message.content.lstrip('c|someone')

    await bot.send_message(channel,'{}{}'.format(random.choice(users).mention, msg))
    # The {} gets replaced by the contents of the format function in their corresponding order

@someone.error
async def someone(error,ctx):
    print(">> Failed c|someone: {}".format(error))
    if isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
    elif isinstance(error, commands.CheckFailure):
        pass
