# StupidBoiBot
Stupid Discord bot that I created because I couldn't find something like it already implemented. 

This bot will join voice channels and play inro music for users. 
It is slightly customizable in its current state and is not super robust.
The bot does NOT work well in large servers with many users joining and leaving voice at once.
Users can DM a .mp3 filet to the bot and it will save it to the sounds folder for them. Check the config file to set size limitations

To get working modify the config.json.default file. BE SURE TO REMOVE THE .default suffix before launching!


config breakdown:
cmd_prefix: The key character to prefix a command such as in the default $COMMAND
user_disabled_intro: An array of users with their intro sound disabled. This can be modified via command
discord_token: This is your bots Discord token.
admin_user: An array of the usernames that have admin privileges with the bot. Can be modified via command
blocked_channels: Voice channels that bot will not follow users into
sound_time: The max time a sound clip can play for. Can be modified via command
no_sound_timer: An array of users with the sound time limit disabled.


commands can be found by using the $help command. Make sure you are in the admin_user list to be able to use all commands!

create a 'sounds' folder in the directory of the script. Add .mp3 files with the username of who it will play for (capitalization counts!)

Reliant on Discord.py and FFmpegPCMAudio dependencies 

I can not gurantee how active I will be in further development of this bot.
