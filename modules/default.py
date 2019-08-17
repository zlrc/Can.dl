# Generic bot commands (mostly).
import discord
from discord.ext import commands
from wax.logger import log
from wax import cmd_info
import random
import os.path
import sqlite3


class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Setting up server groups database
        groups_db = sqlite3.connect(os.path.realpath('./db/groups.db'))

        # Set up a table if one doesn't exist already
        try:
            c = groups_db.cursor()
            c.execute('''CREATE TABLE active_groups
                     (server_name text, server_id integer, role_name text, role_id integer)''')
            groups_db.commit()
            log(">> No groups data table found, generating a new one...", True, type="warning")
            groups_db.close()
        except:
            pass



    @commands.command(pass_context=True)
    async def help(self, ctx):
        """ Pulls up this message. """
        helpmsg = discord.Embed(color=0xe0216a, url=" ", description="All commands must start with **{}** (e.g. *{}help*).".format(self.bot.command_prefix, self.bot.command_prefix))

        helpmsg.set_author(name="🕯️ "+self.bot.user.name+" Commands")
        helpmsg.set_footer(text=" ")

        # Read dictionary in cmd_info.py
        for category in cmd_info.descriptions:
            if category in self.bot.modules: # if the cog is enabled
                title = category.capitalize() + ":"
                desc = ""

                for cmd in cmd_info.descriptions[category]:
                    desc += "`" + cmd + "` - " + cmd_info.descriptions[category][cmd] + "\n"

                helpmsg.add_field(name=title, value=desc)

        # Send the embed
        await self.bot.send_message(ctx.message.author, embed=helpmsg)


    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """ Responds with 'pong!', used to check response time of the bot.  """
        print(">> pong!")
        channel = ctx.message.channel
        await self.bot.send_typing(ctx.message.channel)

        await self.bot.send_message(channel, "pong!")


    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1,8, commands.BucketType.channel)
    async def someone(self, ctx):
        """ Mentions a random user with a message. """
        channel = ctx.message.channel
        users = list(ctx.message.guild.members) # Grabs a dictionary of users on the server, then converts it to a list
        msg = ctx.message.content.lstrip('c|someone')

        await self.bot.send_message(channel,'{}{}'.format(random.choice(users).mention, msg))
        # The {} gets replaced by the contents of the format function in their corresponding order

    @someone.error
    async def someone_error(self, ctx, error):
        log(">> Failed to run c|someone for {}: {}".format(ctx.message.author,error), True, type="error")
        if isinstance(error, commands.CommandOnCooldown):
            await self.bot.send_message(ctx.message.channel,"❌ | **{}**".format(error))
        elif isinstance(error, commands.CheckFailure):
            pass



    # Vanity Roles
    @commands.command(pass_context=True)
    @commands.guild_only()
    async def vrole(self, ctx, func):
        """
        Allows the bot to assign vanity roles to non-admin users.

        Admins can control which roles they want to be considered as
        vanity roles using the 'add' and 'remove' options.

        This command is intended to give non-admin users the ability
        to give themselves roles that they normally would have to ask
        someone else to in order to get them (color roles, teams, etc.)

        In code, vanity roles are referred to as "groups":
        addgroup - Adds roles to the list of groups members can join
        removegroup - Removes roles from the list of groups members can join
        joingroup - Assigns roles that user specifies
        leavegroup - Removes roles that user specifies
        """

        # Python doesn't have case switches, so we're just gonna use a dictionary instead.
        options = {
            "add": self.addgroup,
            "remove": self.removegroup,
            "request": self.joingroup,
            "revoke": self.leavegroup,
            "list": self.listgroups
        }
        await options[func](ctx)


    async def list_guild_roles(self, ctx, message):
        """ Sends a message with all the server's roles listed. """
        await self.bot.send_typing(ctx.message.channel)
        roles = list(ctx.message.guild.roles)
        s = ""

        # Turning the list of roles into a working string, or else the bot just spits out the object ids
        for i in roles[1:]:
            s += str(roles.index(i)) + ": " + str(i) + "\n"

        return await ctx.message.channel.send("```{}```\n{}".format(s, message))

    async def list_guild_vanity_roles(self, ctx, cursor, message):
        """ Sends a message with all the server's vanity roles listed. """
        await self.bot.send_typing(ctx.message.channel)
        s = ""
        i = 1

        # Compile the list of role names
        for row in cursor.execute('SELECT role_name FROM active_groups WHERE server_id=?', (ctx.message.guild.id,)):
            role = str(row)[2:-3] # Strips the parenthesis and comma from the result

            s += str(i) + ": " + role + "\n"
            i += 1

        return await ctx.message.channel.send("```{}```\n{}".format(s, message))

    async def get_vroles_data(self, ctx, cursor):
        """ Returns a list containing the server's vanity role IDs """
        roles_list = [None]
        c = cursor

        # Gather all the available role IDs into the list above
        for row in c.execute('SELECT role_id FROM active_groups WHERE server_id=?', (ctx.message.guild.id,)):
            roles_list.append(int(str(row)[1:-2])) # 'row' variable shows up as '()' if not converted to a string first.

        return roles_list

    async def update_groupsdb(self, ctx):
        """ Cleans out any roles in the db that have since been deleted from the server. """
        conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
        c = conn.cursor()

        role_ids = await self.get_vroles_data(ctx, c)
        for i in role_ids:
            if not discord.utils.get(ctx.message.guild.roles, id=i): # role no longer exists
                c.execute('DELETE FROM active_groups WHERE role_id=?', (i,))
                conn.commit()
        conn.close()


    async def addgroup(self, ctx):
        """ Adds new vanity roles for the server to the database """
        bot = self.bot
        has_perm = ctx.message.author.guild_permissions

        # Check if they have the right permissions
        if not (has_perm.manage_roles and has_perm.ban_members):
            raise commands.MissingPermissions(['manage_roles', 'ban_members'])

        def is_author(m):
            return (m.author == ctx.message.author) and (m.channel == ctx.message.channel)

        # Prompt the user
        rolelist = await self.list_guild_roles(ctx, "🗒️ | **Type the role number(s) you would like to mark as vanity roles. Seperate numbers with a comma if there are multiple. Otherwise, type **`cancel`** to quit.**")
        try:
            msg = await bot.wait_for('message', check=is_author, timeout=60)
        except:
            await ctx.message.channel.send("❌ | **Canceled** `c|vrole` **execution: {} took too long to respond.**".format(ctx.message.author))
            await rolelist.delete()
            return
        roles = list(ctx.message.guild.roles)

        # Checks user response, then saves groups to database if valid.
        if msg.clean_content.lower() == "cancel":
            await bot.send_message(ctx.message.channel, "**Canceled!**")
            await rolelist.delete()
            return
        else:
            conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
            c = conn.cursor()

            try:
                nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                print(">> {} created new group(s):".format(ctx.message.author))

                # Using index numbers, we'll save information on selected roles to our database
                for n in nums:
                    await bot.send_typing(ctx.message.channel)
                    role_data = (ctx.message.guild.name, ctx.message.guild.id, roles[n].name, roles[n].id)

                    # Check if role has been added already
                    c.execute('SELECT role_id FROM active_groups WHERE role_id=?', (roles[n].id,))

                    if not c.fetchone(): # If it doesn't exist, insert the group info as a new row
                        c.execute('INSERT INTO active_groups VALUES (?,?,?,?)', role_data)
                        conn.commit()
                        print("  {}".format(roles[n]))
                    else:
                        print("  {} [ALREADY EXISTS]".format(roles[n].name))

                await bot.send_message(ctx.message.channel,"🗒️ | **Successfully added the selected vanity roles! Type **`c|vrole list`** to view them.**")

            except ValueError:
                log(">> {} tried adding vanity roles, but the command failed due to invalid arguments.".format(ctx.message.author), True, type="warning")
                await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

            finally:
                await rolelist.delete()
                conn.close()

    async def removegroup(self, ctx):
        """ Deletes vanity roles for the server from the database """
        bot = self.bot
        has_perm = ctx.message.author.guild_permissions
        await self.update_groupsdb(ctx)

        # Check if they have the right permissions
        if not (has_perm.manage_roles and has_perm.ban_members):
            raise commands.MissingPermissions(['manage_roles', 'ban_members'])

        def is_author(m):
            return (m.author == ctx.message.author) and (m.channel == ctx.message.channel)


        # Connect to the database and get the data we need
        conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
        c = conn.cursor()

        grouplist = await self.get_vroles_data(ctx, c)
        log(">> Role ids for this server: {}".format(grouplist))

        rolelist = await self.list_guild_vanity_roles(ctx,c,"🗒️ | **Type the role numbers you would like to remove, seperate numbers with a comma if removing more than one. Otherwise, type **`cancel`** to quit.**")
        try:
            msg = await bot.wait_for('message', check=is_author, timeout=45)
        except:
            await ctx.message.channel.send("❌ | **Canceled** `c|vrole` **execution: {} took too long to respond.**".format(ctx.message.author))
            await rolelist.delete()
            conn.close()
            return


        # Checks user response, then removes groups from database if valid.
        if msg.clean_content.lower() == "cancel":
            await bot.send_message(ctx.message.channel, "**Canceled!**")
            await rolelist.delete()
            conn.close()
        else:
            try:
                nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                print(">> {} removed groups:".format(ctx.message.author))

                for n in nums: # Deletes one row at a time
                    await bot.send_typing(ctx.message.channel)
                    c.execute('DELETE FROM active_groups WHERE role_id=?', (grouplist[n],))
                    conn.commit()
                    print("  {} | {}".format(discord.utils.get(ctx.message.guild.roles, id=int(grouplist[n])),grouplist[n]))

                await bot.send_message(ctx.message.channel,"🗒️ | **Successfully removed the selected vanity roles! Type **`c|vrole list`** to view them.**")

            except ValueError:
                log(">> {} tried removing vanity roles, but the command failed due to invalid arguments.".format(ctx.message.author), True, type="warning")
                await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

            finally:
                await rolelist.delete()
                conn.close()

    async def joingroup(self, ctx):
        """ Gives the invoker vanity roles """
        bot = self.bot
        botperms = ctx.message.channel.permissions_for(ctx.message.guild.me)
        await self.update_groupsdb(ctx)

        def is_author(m):
            return (m.author == ctx.message.author) and (m.channel == ctx.message.channel)

        if botperms.manage_roles:
            # Connect to the database and get the data we need
            conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
            c = conn.cursor()

            grouplist = await self.get_vroles_data(ctx, c)
            log(">> {}".format(grouplist))

            rolelist = await self.list_guild_vanity_roles(ctx,c,"🗒️ | **Type the role numbers you would like to have, seperate numbers with a comma if there's more than one. Otherwise, type **`cancel`** to quit.**")
            try:
                msg = await bot.wait_for('message', check=is_author, timeout=45)
            except:
                await ctx.message.channel.send("❌ | **Canceled** `c|vrole` **execution: {} took too long to respond.**".format(ctx.message.author))
                await rolelist.delete()
                conn.close()
                return


            # Checks user response, joins groups if valid.
            if msg.clean_content.lower() == "cancel":
                await bot.send_message(ctx.message.channel, "**Canceled!**")
                await rolelist.delete()
                conn.close()
            else:
                try:
                    nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                    print(">> {} joined the following groups:".format(ctx.message.author))

                    for n in nums:
                        grouprole = discord.utils.get(ctx.message.guild.roles, id=int(grouplist[n])) # Finding the role by ID
                        await ctx.message.author.add_roles(grouprole, reason="c|vrole command invoke")
                        print("  {}".format(grouprole))

                    await bot.send_message(ctx.message.channel,"🗒️ | **Successfully granted role(s)!**")

                except ValueError:
                    log(">> {} tried obtaining vanity roles, but the command failed due to invalid arguments.".format(ctx.message.author), True, type="warning")
                    await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

                finally:
                    await rolelist.delete()
                    conn.close()
        else:
            await bot.send_message(ctx.message.channel,"❌ | **Error! I do not have permission to manage roles!**")

    async def leavegroup(self, ctx):
        bot = self.bot
        botperms = ctx.message.channel.permissions_for(ctx.message.guild.me)
        await self.update_groupsdb(ctx)

        def is_author(m):
            return (m.author == ctx.message.author) and (m.channel == ctx.message.channel)

        if botperms.manage_roles:
            # Connect to the database and get the data we need
            conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
            c = conn.cursor()

            grouplist = await self.get_vroles_data(ctx, c)
            log(">> {}".format(grouplist))

            rolelist = await self.list_guild_vanity_roles(ctx,c,"🗒️ | **Type the role numbers you would like to revoke, seperate numbers with a comma if removing more than one. Otherwise, type **`cancel`** to quit.**")
            try:
                msg = await bot.wait_for('message', check=is_author, timeout=45)
            except:
                await ctx.message.channel.send("❌ | **Canceled** `c|vrole` **execution: {} took too long to respond.**".format(ctx.message.author))
                await rolelist.delete()
                conn.close()
                return


            # Checks user response, leaves groups if valid.
            if msg.clean_content.lower() == "cancel":
                await bot.send_message(ctx.message.channel, "**Canceled!**")
                await rolelist.delete()
                conn.close()
            else:
                try:
                    nums = [int(s) for s in msg.clean_content.split(',')] # Converts string of numbers to a list of integers
                    print(">> {} left the following groups:".format(ctx.message.author))

                    for n in nums:
                        grouprole = discord.utils.get(ctx.message.guild.roles, id=int(grouplist[n])) # Finding the role by ID
                        await ctx.message.author.remove_roles(grouprole, reason="c|vrole command invoke")
                        print("  {}".format(grouprole))

                    await bot.send_message(ctx.message.channel,"🗒️ | **Successfully unassigned role(s)!**")

                except ValueError:
                    log(">> {} tried unassigning vanity roles, but the command failed due to invalid arguments.".format(ctx.message.author), True, type="warning")
                    await bot.send_message(ctx.message.channel,"❌ | **Error! That is not a valid response!**")

                finally:
                    await rolelist.delete()
                    conn.close()
        else:
            await bot.send_message(ctx.message.channel,"❌ | **Error! I do not have permission to manage roles!**")

    async def listgroups(self, ctx):
        """ Lists the server's current vanity roles """
        print(">> {} listed the groups!".format(ctx.message.author))
        await self.update_groupsdb(ctx)

        conn = sqlite3.connect(os.path.realpath('./db/groups.db'))
        c = conn.cursor()

        await self.list_guild_vanity_roles(ctx,c,"🗒️ | **Here are the vanity roles available for this server.**")
        conn.close()

    @vrole.error
    async def vrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.message.channel.send("❌ | **Access Denied. {}**".format(error))
            log("Denied {} access to c|group: {}".format(ctx.message.author,error),type="warning")
        else:
            log(">> A c|vrole command was executed, but it failed: {}".format(error), True, type="error")
            log(type="trace")
            await self.bot.send_message(ctx.message.channel,
                "❌ | **Invalid Syntax. Proper usage:** `c|vrole option` **(options: **`add`**, **`remove`**, **`request`**, **`revoke`**, **`list`**)**")




def setup(bot):
    bot.add_cog(Default(bot))
