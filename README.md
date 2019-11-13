# StupidBoiBot
Stupid Discord bot 
This bot will join voic channels and play inro music for users. 
It is slightly customizable in its current state and is not super robust.
The bot does NOT work well in large servers with many users joining and leaving voice at once.

To get working modify the config.json.default file. BE SURE TO REMOVE THE .default suffix before launching!

config breakdown:
cmd_prefix: The key character to prefix a command such as in the default $COMMAND
user_disabled_intro: An array of users with their intro sound disabled. This can be modified via command
discord_token: This is your bots Discord token.
admin_user: An array of the usernames that have admin privileges with the bot. Can be modified via command
blocked_channels: Voice channels that bot will not follow users into
sound_time: The max time a sound clip can play for. Can be modified via command
no_sound_timer: An array of users with the sound time limit disabled.