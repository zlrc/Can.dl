<p align="center">
  <img src="https://imgur.com/tF9Gz3I.png" height=350px>
</p>

# Can.dl Discord Bot
A personal, niche-purpose bot with features intended to fit specific needs of small to moderate-sized servers. Works best when paired with another bot that comes with a standard set of commands.

## Notable Features
`c|group join/leave`: Allows users to give themselves decorative roles without having to ask someone with a "Manage Roles" permission each time. Admins can choose which roles users are allowed to give themselves.

![groups]

`c|invite`: Creates an embed that's customized to look like an invite card for people to RSVP with. Users can configure embed colors, user limit, and embed images with this command. Management tools for invite creators will be added in the future.

![invite]

`c|countdown`: Starts a customized countdown timer. Longer countdowns aren't as accurate in this command's current state, but it works.

![countdown]

## How to Invite
Can.dl is a little bot with little power. Since the machine that it's hosted on isn't all that powerful, the bot is currently limited to private access. What this means for you is that you gotta ask politely for me to invite the bot to your server. Otherwise, you're free to use the source code provided here to set up your own bot, granted that you know how to do that.

## Hosting your own Bot
The code for this bot runs on Python 3. You should be allowed to use the code freely under the license that's included for your own bot. For in-depth help on how to actually make a discord bot, I'd suggest looking up [online tutorials](https://medium.com/@moomooptas/how-to-make-a-simple-discord-bot-in-python-40ed991468b4) and the [discord.py documentation](https://discordpy.readthedocs.io/en/latest/api.html) rather than here.

### Dependencies:
- Python 3
- [discord.py](https://github.com/rapptz/discord.py)
- [markovify](https://github.com/jsvine/markovify)

<i style="font-size: 10.5pt; color: rgb(200,0,0)">* Please let me know if there are any other dependencies that I need to include.</i>

**For Linux users -** I would suggest creating a .desktop launcher with something like the following code to make it easier to launch the bot at the click of a mouse button:

    [Desktop Entry]
    Version=1.0
    Type=Application
    Name=Run Bot
    Comment=
    Exec=python3 run.py
    Icon=discord
    Path=/home/filepath/of/the/bot
    Terminal=true
    StartupNotify=false

[groups]: https://imgur.com/NyXfOPq.png
[invite]: https://imgur.com/bLVCJet.png
[countdown]: https://imgur.com/SbJ4Rwy.png
