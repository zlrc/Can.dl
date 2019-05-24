<p align="center">
  <img src="https://imgur.com/tF9Gz3I.png" height=350px>
</p>

# Can.dl Discord Bot
A personal, niche-purpose bot with features intended to fit specific needs of small to moderate-sized servers. Works best when paired with another bot that comes with a standard set of commands.

## Notable Features
`c|group join/leave`: Allows users to give themselves decorative roles without having to ask someone with a "Manage Roles" permission each time. Admins can choose which roles users are allowed to give themselves.

<p align="center"><img src="https://imgur.com/NyXfOPq.png"></p>

`c|invite`: Creates an embed that's customized to look like an invite card for people to RSVP with. Users can configure embed colors, user limit, and embed images with this command. Management tools for invite creators will be added in the future.

<p align="center"><img src="https://imgur.com/bLVCJet.png"></p>

`c|countdown`: Starts a customized countdown timer. Longer countdowns aren't as accurate in this command's current state, but it works.

<p align="center"><img src="https://imgur.com/SbJ4Rwy.png"></p>

## How to Invite
Can.dl is a little bot with little power. Since the machine that it's hosted on isn't all that powerful, the bot is currently limited to private access. You're free to use the source code provided here to set up your own bot though, granted that you know how to do that.

## Hosting your own Bot
The code for this bot runs on Python 3. You should be allowed to use the code freely under the license that's included for your own bot. For in-depth help on how to actually make a discord bot, I'd suggest looking up [online tutorials](https://medium.com/@moomooptas/how-to-make-a-simple-discord-bot-in-python-40ed991468b4) and the [discord.py documentation](https://discordpy.readthedocs.io/en/latest/api.html) rather than here.

Once you're all set up, run `run.py` to boot up the bot.

### Dependencies:
- Python 3
- [discord.py](https://github.com/rapptz/discord.py)
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/#Download)
- [Markovify](https://github.com/jsvine/markovify)
- [Pillow](https://pillow.readthedocs.io/en/stable/installation.html)

<i style="font-size: 10.5pt; color: rgb(200,0,0)">* Please let me know if there are any other dependencies that I need to include.</i>

[groups]: https://imgur.com/NyXfOPq.png
[invite]: https://imgur.com/bLVCJet.png
[countdown]: https://imgur.com/SbJ4Rwy.png
