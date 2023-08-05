# New Docker image available!
See the new section DOCKER at the bottom of the read me for more information

# StupidBoiBotV2
*Stupid Discord bot that I created because I couldn't find something like it already implemented.* <br>
*StupidBoiBotV2 converts this bot from a personal project with spaghetti code and lots of issues into a more refined, readable, functional, and feature filled bot. It's far from perfect and I can't gurantee the speed at which it will advance; however any and all issues should be brought up via Github or through a direct message to me on Discord at `IAmFatAndLazy#9850`* <br><br>
**If you are updating from V1 you MUST run the `Migrate` command as a bot admin to update the sounds folder file structure to support V2. Only the folder names will be changes which will preserve all users sound files.**<br><br>

This bot will join voice channels and play intro music for users.        
The bot does **NOT** work well in large servers with many users joining and leaving voice at once.
This is due to the limitation that it can only join one voice channel at a time.
Users are able to add and remove .mp3's via DM's to the bot. If a user has more than one sound file
the bot will choose one from random to play when they enter. Designed with all interaction with the bot to be via DM.
If your commands are not working it is probably because you are not direct messaging the bot!


## Install
- Download or clone the git repository somewhere you can access it
- Install the dependencies as described in the `Dependencies` section
- Create a bot using the Discord developer web portal as seen [here](https://discordpy.readthedocs.io/en/latest/discord.html)<br>
**Note: The minimum bot permissions integer is 36703232**
- Modify the `config.json.default` file as described in the `Configuration` section<br>
**NOTE: Be sure to remove the `.default` suffix before launching the bot**
- Launch the `StupidBoiV2.py` script via the `WindowsLaunchBot`, `BashLaunchBot` or other means


## Commands
**COMMANDS CAN ALSO BE VIEWED BY USING THE HELP COMMAND**
#### All commands will only work if direct messaged to the bot unless otherwise stated:
###### Admin Commands:
 - **AddAdmin:**         (Admin) Add another admin user. Uses account DiscordID NOT Username!
 - **ToggleSoundTimer:**  (Admin) Toggles a users max time limit on their sound files
 - **BlockedChannels:**   (Admin) (Admin) Lists channels the bot is currently blocked from entering. Add a channel name after the command to add/remove a channel from this list.
 - **ListAdmins:**        (Admin) View the list of admins
 - **MaxFileSize:**       (Admin) Sets maximum file size bot will accept for sound files
 - **MaxFilesAllowed:**   (Admin) Sets maximum amount of files bot will allow users to have at once
 - **Migrate:**           (Admin) Migrates all users sound folders to new naming scheme
 - **ReloadConfig:**      (Admin) Reloads configuration file manually
 - **RemoveAdmin:**       (Admin) Remove another admin user
 
 ###### All User Commands
 - **Silence:**           Silences the bot if it is currently playing audio (works anywhere)
 - **help:**              Shows this help dialog. add a command as a parameter for more info (works anywhere)<br><br>
 
 - **Intro:**             Toggles your intro sound on/off
 - **AddSound:**          Attach a .mp3 file with this command as a comment to add it to your sounds folder
 - **RemoveSound:**       Use in conjunction with MySound to delete some of your sound files. Accepts the filename or index of the sound to be deleted.
 - **MySounds:**          Show your indexed sound files
 



## Configuration

#### Config requirements
You **MUST** add your Discord token into the `discord_token` section. Replace the `BOT_DISCORD_TOKEN` string with your token<br>
**The line should like as such `"discord_token": "1981951afasf5875x15489",`** <br><br>
The rest of this file **CAN** be left as it and the bot will run. However, you will not be able to access the admin commands without
adding your userID into the `admin_user` variable. You can manually get your userID as shown [here](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)<br>
The rest of the config can be altered through the bot; however you can make any changes manually as well.

#### Config breakdown

- `cmd_prefix` - The character to prefix a command such as in the default $COMMAND
- `user_disabled_intro` - A list of users with their intro sound disabled. This can be modified via command
- `max_file_size` - The maximum size of audio files the bot will accept from users stored in bytes. This can be modified via command
- `discord_token` - This is your bots Discord token. Find how to get a bot token [here](https://discordpy.readthedocs.io/en/latest/discord.html).
- `admin_user` - A list of the userID's that have admin privileges with the bot. This can be modified via command. Find out how to manually get userID's [here] (https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)
- `blocked_channels` - Voice channels that bot will not follow users into. This can be modified via command
- `sound_time` - The max time a sound clip can play for before the bot stops. This can be modified via command
- `no_sound_timer` - A list of userID's with the sound time limit disabled. This can be modified via command
- `max_sound_files` - The amount of sound files each user can upload through the bot. This can be modified via command


Commands can be found by using the `help` command.     
Make sure you are in the `admin_user` list to be able to use all commands! The first admin user must be added manually to the config file!


### Dependencies
- `Discord.py` 
- `FFmpegPCMAudio`  Make sure this is added to your system path!
- `PyNacl`
- 
You can use `pip install discord.py pynacl` to get those two packages.<br>
FFMpeg can be acquired from their website [here](https://www.ffmpeg.org/download.html) 

## Docker

I haven't touched this project in a long while but I was looking to move this bot into a docker image so I could move it more easily through my current infrastructure. As such, there is now a Dockerfile in this git repo for you to build yourself, or an image on Dockerhub for you to pull down! You can get the docker image (along with instructions on running the bot) over there at https://hub.docker.com/r/iamfatandlazy/stupidboiv2

As I state in the instructions on Dockerhub, this simplified the build by a large margin. I take care of getting you setup with all the dependencies and OS and all you need to do is configure your config.json and point one Docker volume at it, and then point a second Docker volume to a location the bot can save it's sounds too. As I write this it is almost 2AM, so I will try to get a few screenshots or screen recording of the new process soon.


*I can not gurantee how active I will be in further development of this bot.*
