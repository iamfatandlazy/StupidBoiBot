# StupidBoi5000.py
# My bot that will do many many dumb things

import os
import sys
import random
import asyncio

import discord
from discord.ext import commands
from discord.voice_client import VoiceClient

import json

#read config from file
#get file directory to script and config file
fileDir = sys.path[0]
config_file = open(fileDir+'/config.json')
data=json.load(config_file)
	
#assign values to vars	
token = data['discord_token']
adminUsers = data['admin_user']
cmdPrefix = data['cmd_prefix']
soundTime = data['sound_time']
noSoundTimer = data['no_sound_timer']
disabledIntros = data['user_disabled_intro']
blockedChannels = data['blocked_channels']


#setup discord client
#client = discord.Client()

#setup commands
bot = commands.Bot(command_prefix=cmdPrefix)

print('David\'s StupidBot5000 launching...')

@bot.event
async def on_ready():
	print('{} has connected to Discord!'.format(bot.user))
	await bot.change_presence(activity=discord.Game(name='$help'))
		

#when user moves channel play their intro sound
@bot.event
async def on_voice_state_update(member,before,after):		
	if ((after.channel is not None)and(len(bot.voice_clients)==0)):
		refresh_config()
		disabledIntros = data['user_disabled_intro']
		if ((before.channel!=after.channel)and(check_channel_if_allowed(after.channel.name))and(member.name not in disabledIntros)):
			currentChannel=after.channel
			await currentChannel.connect()
			vcVal = 0
			for i, vc in enumerate(bot.voice_clients):
				if vc.guild==member.guild:
					vcVal = i
			if not bot.voice_clients[vcVal].is_playing():
				bot.voice_clients[vcVal].play(discord.FFmpegPCMAudio(fileDir+'/sounds/{}.mp3'.format(member.name)))
				print('Playing {}\'s intro sound!'.format(member.name))
				timer = 0
				enabledTimer = True
				if has_no_sleep_timer(member.name)==True:
					enabledTimer = False
				while (bot.voice_clients[vcVal].is_playing()and(timer<=int(soundTime))):
					await asyncio.sleep(1)
					if enabledTimer==True:
						timer+=1
				await bot.voice_clients[vcVal].disconnect()

#checks if bot is playing sound, then stops it
@bot.command(name='silence', help='Silences bot if currently playing audio')
async def silence_bot(ctx):
	vcVal = 0
	await ctx.message.delete()
	for i, vc in enumerate(bot.voice_clients):
		if vc.guild==ctx.guild:
			vcVal = i
	if bot.voice_clients[vcVal].is_playing():
		bot.voice_clients[vcVal].stop()
		print('Silencing bot')
		
#add/remove user from disabled intro's list		
@bot.command(name='intro', help='Toggles your intro sound on/off')
async def intro_toggle(ctx):
	global disabledIntros
	user = ctx.author.name
	await ctx.message.delete()
	if user in disabledIntros:
		disabledIntros.remove(user)
		update_JSON('user_disabled_intro',disabledIntros)
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		await dm.send('You have enabled your intro song! Lets make you a star!')
	else:
		disabledIntros.append(user)
		update_JSON('user_disabled_intro',disabledIntros)
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		await dm.send('You have disabled your intro song! Back to your boring ordinary entrance!')

#adminUsers can change the length of sound clips allowed to play
@bot.command(name='maxSound', help='Sets max time sound file will play in seconds')
async def set_max_sound(ctx, time):
	global soundTime
	await ctx.message.delete()
	dm = ctx.author.dm_channel
	if dm is None:
		await ctx.author.create_dm()
		dm = ctx.author.dm_channel
	if ctx.message.author.name in adminUsers:
		update_JSON("sound_time",time)
		soundTime = data['sound_time']
		print('Set max sound to {}'.format(time))
		await dm.send('Set max sound to {}'.format(time))
	else:
		await dm.send('You do not have permissions to use this command!')
		print('{} tried to use maxSound command'.format(ctx.author.name))
		
		
#adminUsers can change the length of sound clips allowed to play
@bot.command(name='maxTimer', help='Toggles the maxTimer for user')
async def set_max_sound(ctx, user):
	global noSoundTimer
	await ctx.message.delete()
	dm = ctx.author.dm_channel
	if dm is None:
		await ctx.author.create_dm()
		dm = ctx.author.dm_channel
	if ctx.message.author.name in adminUsers:
		if user not in noSoundTimer:
			noSoundTimer.append(user)
			print('Toggled {}\'s max sound timer off'.format(user))
			await dm.send('Toggled {}\'s max sound timer off'.format(user))
		elif user in noSoundTimer:
			noSoundTimer.remove(user)
			print('Toggled {}\'s max sound timer on'.format(user))
			await dm.send('Toggled {}\'s max sound timer on'.format(user))
		update_JSON("no_sound_timer",noSoundTimer)
		refresh_config
		soundTime = data['no_sound_timer']
	else:
		await dm.send('You do not have permissions to use this command!')
		print('{} tried to use maxTimer command'.format(ctx.author.name))
		

#if admin uses command, will add user to bot admin list		
@bot.command(name='AddAdmin', help='Allows admin user to add another admin user')
async def add_admin(ctx, _name):
	global adminUsers
	await ctx.message.delete()
	if ((ctx.message.author.name in adminUsers)and(_name not in adminUsers)):
		adminUsers.append(_name)
		update_JSON("admin_user",adminUsers)
		refresh_config()
		adminUsers = data['admin_user']
		print('Added {} to admin list'.format(_name))
	else:
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		if _name in adminUsers:
			await dm.send('{} is already an admin.'.format(_name))
		else:
			await dm.send('You do not have permissions to use this command!')
			print('{} tried to use AddAdmin command'.format(ctx.author._name))
		
##if admin uses command, will remove user to bot admin list		
@bot.command(name='RemoveAdmin', help='Allows admin user to remove another admin user')
async def remove_admin(ctx, _name):
	global adminUsers
	await ctx.message.delete()
	if ((ctx.message.author.name in adminUsers)and(_name in adminUsers)and(ctx.message.author.name!=_name)):
		adminUsers.remove(_name)
		update_JSON("admin_user",adminUsers)
		refresh_config()
		adminUsers = data['admin_user']
		print('Removed {} to admin list'.format(_name))
	else:
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		if _name==ctx.message.author.name:
			await dm.send('You can\'t remove yourself as admin via this command.'.format(_name))
		else:
			await dm.send('You do not have permissions to use this command!')
			print('{} tried to use RemoveAdmin command'.format(ctx.author._name))
			
@bot.command(name='BlockedChannels', help='Lists channels the bot is currently blocked from entering')
async def blocked_channels(ctx, channel=None):
	global blockedChannels
	refresh_config()
	blockedChannels = data['blocked_channels']
	await ctx.message.delete()
	dm = ctx.author.dm_channel
	if dm is None:
		await ctx.author.create_dm()
		dm = ctx.author.dm_channel
	if ctx.message.author.name in adminUsers:
		if channel is not None:
			if channel in blockedChannels:
				blockedChannels.remove(channel)
				update_JSON('blocked_channels',blockedChannels)
				refresh_config()
				blockedChannels = data['blocked_channels']
				await dm.send('Removed {} from blocked channels list'.format(channel))
				print ('Removed {} from blocked channels list'.format(channel))
				
			else:
				blockedChannels.append(channel)
				update_JSON('blocked_channels',blockedChannels)
				refresh_config()
				blockedChannels = data['blocked_channels']
				await dm.send('Added {} to blocked channels list'.format(channel))
				print ('Added {} to blocked channels list'.format(channel))
		else:
			tmpString = ''
			for entry in blockedChannels:
				tmpString = tmpString + '{}\n'.format(entry)
			await dm.send('Blocked channels:\n\n{}'.format(tmpString))
		
	else:
		await dm.send('You do not have permissions to use this command!')
		print('{} tried to use BlockedChannels command'.format(ctx.author._name))
		

		
#checks if name is in no sleep timer list, if so return True
def has_no_sleep_timer(name):
	global noSoundTimer
	global data
	refresh_config()
	noSoundTimer = data['no_sound_timer']
	for user in noSoundTimer:
		if name==user:
			return True
	return False
				
#checks if channel name is in blocked channels list and returns false if it is				
def check_channel_if_allowed(channelName):
	global clockedChannels
	refresh_config()
	blockedChannels=data['blocked_channels']
	
	for	channel in blockedChannels:
		if channelName.lower()==channel.lower():
			return False
	return True

#refreshes our config file for getting updated values    
def refresh_config():
	global data
	global config_file
	config_file.close()
	config_file = open(fileDir+'/config.json')
	data=json.load(config_file)

#for updating JSON fields and writting them to file
def update_JSON(key, newVal):
	global data
	global fileDir
	data[key] = newVal
			
	wFile = open(fileDir+'/config.json','w')
	json.dump(data,wFile,indent = 2)	
	wFile.close()
	refresh_config()

def is_admin(name):
	refresh_config()
	adminUsers = data['admin_user']
	for user in admin_user:
		if user==name:
			return True
	return False
	
@bot.event
async def on_client_error(ctx, error):
    if isinstance(error, discord.ClientException):
        print('already connected!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    
            
bot.run(token)

