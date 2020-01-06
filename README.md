<p align="center">
  <img src="https://user-images.githubusercontent.com/30582227/71788525-01ed6d00-2fd8-11ea-9a63-4996beee8a75.png" height=350px>
</p>

---

A personal, niche-purpose Discord bot. Mostly comes with entertainment features, so it works best when paired with other bots.

---

## Notable Features
Can.dl uses the `c|` prefix for all of it's commands.

`c|vrole request/revoke`: Allows users to give themselves vanity roles without having to ask someone with a "Manage Roles" permission each time. Admins can choose which roles users are allowed to give themselves.

<p align="center"><img src="https://user-images.githubusercontent.com/30582227/71790656-6adbe180-2fe6-11ea-991a-cf2b94c7a6f8.gif"></p>

`c|invite`: Creates an embed that's customized to look like an invite card for people to RSVP with. Users can configure embed colors, user limit, and embed images with this command. Management tools for invite creators will be added in the future.

<p align="center"><img src="https://user-images.githubusercontent.com/30582227/71790658-6b747800-2fe6-11ea-82ab-2cdfe73dcdf5.gif"></p>

`c|countdown`: Starts a customized countdown timer. The amount of timers running at the same time is limited to one per server.

<p align="center"><img src="https://user-images.githubusercontent.com/30582227/71790519-bfcb2800-2fe5-11ea-9640-9f7af171fb8d.gif"></p>

**Overlays** - Type `c|overlays` to see a list of overlay commands available for this bot. If hosting your own instance of the bot, edit `overlays.py` to add your own custom overlays.

**Markov Chains** - `c|markov` uses "AI Magic" to string together new messages using those that exist on the server. The command takes `@mention` parameters to specify a user or channel to generate messages from.

**Fill-in-the-Blanks** - Start a game of Mad Libs by typing `c|madlib`. See the examples in `/db/madlibs` to learn how you can create your own!

## How to Invite
Can.dl is currently limited to private access, but you're free to use the source code provided here to host your own! Granted, it must use a different name and avatar to avoid confusion.

## Hosting your own Bot
The code for this bot runs on **Python 3**. You should be allowed to use the code freely under the license that's included. For in-depth help on how to actually make a discord bot, I'd suggest looking up [online tutorials](https://medium.com/@moomooptas/how-to-make-a-simple-discord-bot-in-python-40ed991468b4) and the [discord.py documentation](https://discordpy.readthedocs.io/en/latest/api.html) rather than here.

Once all the Discord API stuff is configured, type `python3 run.py` in your command line to boot up the bot.

### Dependencies:
- Python 3
- [discord.py](https://github.com/rapptz/discord.py)
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/#Download)
- [Markovify](https://github.com/jsvine/markovify)
- [Pillow](https://pillow.readthedocs.io/en/stable/installation.html)

See `requirements.txt` for a full list of required Python packages and their respective versions.

## Licensing
[![MIT License](https://img.shields.io/badge/License-MIT-blue)](https://github.com/zlrc/Can.dl/blob/master/LICENSE)
