# StupidBoi5000.py
# Author: IAmFatAndLazy

from datetime import datetime
import os
import sys
import random
import asyncio

import discord
from discord.ext import commands
from discord.voice_client import VoiceClient

import json
import random


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
fileSizeAllowed = data['max_file_size']
maxSoundFiles = data['max_sound_files']


#setup discord client
#client = discord.Client()

#setup commands
bot = commands.Bot(command_prefix=cmdPrefix)

print('IAmFatAndLazy\'s StupidBot5000 launching...')


@bot.event
async def on_ready():
	print('Checking for sounds folder')
	if (os.path.exists(fileDir+'/sounds/')):
		print('Sounds folder found!')
	else:
		os.mkdirs(fileDir+'/sounds')
		print('No sounds folder found. Creating one now')
	print('{} has connected to Discord!'.format(bot.user))
	await bot.change_presence(activity=discord.Game(name='$help'))
		

#when user moves channel play their intro sound
@bot.event
async def on_voice_state_update(member,before,after):		
	if ((after.channel is not None)and(len(bot.voice_clients)==0)and (member.bot==False)):
		refresh_config()
		user = member.name.lower()+'#'+member.discriminator 
		if ((before.channel!=after.channel)and(check_channel_if_allowed(after.channel.name))and(user not in disabledIntros)and(os.path.exists(fileDir + '/sounds/' + user))and(len(os.listdir(fileDir+'/sounds/'+user))>0)):
			currentChannel=after.channel
			await currentChannel.connect()
			vcVal = 0
			for i, vc in enumerate(bot.voice_clients):
				if vc.guild==member.guild:
					vcVal = i
			if not bot.voice_clients[vcVal].is_playing():
				#choose a random sound from their sound folder to play
				files = os.listdir(fileDir+'/sounds/'+user)
				bot.voice_clients[vcVal].play(discord.FFmpegPCMAudio(fileDir+'/sounds/'+user+'/'+random.choice(files)))
				print('{} Playing {}\'s intro sound!'.format(datetime.now(), member.name))
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
	user = ctx.author.name+'#'+ctx.author.discriminator
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
@bot.command(name='maxSound', help='Sets the max time sound file will play in seconds.')
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
		
		
#adminUsers can toggle the sound timer for users
@bot.command(name='maxTimer', help='Toggles the time limit for users sound on or off.')
async def set_max_sound(ctx, user):
	global noSoundTimer
	await ctx.message.delete()
	dm = ctx.author.dm_channel
	if dm is None:
		await ctx.author.create_dm()
		dm = ctx.author.dm_channel
	if isAdmin(ctx.message.author):
		if user not in noSoundTimer:
			noSoundTimer.append(user)
			print('Toggled {}\'s max sound timer off'.format(user))
			await dm.send('Toggled {}\'s max sound timer off'.format(user))
		elif user in noSoundTimer:
			noSoundTimer.remove(user)
			print('Toggled {}\'s max sound timer on'.format(user))
			await dm.send('Toggled {}\'s max sound timer on'.format(user))
		update_JSON("no_sound_timer",noSoundTimer)
		refresh_config()
	else:
		await dm.send('You do not have permissions to use this command!')
		print('{} tried to use maxTimer command'.format(ctx.author.name))
		

#if admin uses command, will add user to bot admin list		
@bot.command(name='AddAdmin', help='Allows admin users to add another admin user. Make sure to add the discord ID!')
async def add_admin(ctx, _name):
	global adminUsers
	await ctx.message.delete()
	if ((isAdmin(ctx.message.author))and(_name.lower() not in (name.lower() for name in adminUsers))):
		adminUsers.append(_name.lower())
		update_JSON("admin_user",adminUsers)
		refresh_config()
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
		
#if admin uses command, will remove user to bot admin list		
@bot.command(name='RemoveAdmin', help='Allows admin user to remove another admin user')
async def remove_admin(ctx, _name):
	global adminUsers
	await ctx.message.delete()
	if ((isAdmin(ctx.message.author))and(_name.lower() in (name.lower() for name in adminUsers))):
		adminUsers.remove(_name.lower())
		update_JSON("admin_user",adminUsers)
		refresh_config()
		print('Removed {} to admin list'.format(_name))
	else:
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		else:
			await dm.send('You do not have permissions to use this command!')
			print('{} tried to use RemoveAdmin command'.format(ctx.author._name))

			
@bot.command(name='BlockedChannels', help='Lists channels the bot is currently blocked from entering')
async def blocked_channels(ctx, channel=None):
	global blockedChannels
	global data
	refresh_config()
	await ctx.message.delete()
	dm = ctx.author.dm_channel
	if dm is None:
		await ctx.author.create_dm()
		dm = ctx.author.dm_channel
	if isAdmin(ctx.message.author):
		if channel is not None:
			if channel in blockedChannels:
				blockedChannels.remove(channel)
				update_JSON('blocked_channels',blockedChannels)
				refresh_config()
				await dm.send('Removed {} from blocked channels list'.format(channel))
				print ('Removed {} from blocked channels list'.format(channel))
				
			else:
				blockedChannels.append(channel)
				update_JSON('blocked_channels',blockedChannels)
				refresh_config()
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

@bot.command(name='MaxFileSize', help='Sets max file size bot will accept for your intro sound')
async def max_file_size(ctx, size):
	global fileSizeAllowed
	global data
	await ctx.message.delete()
	dm = ctx.author.dm_channel
	if dm is None:
		await ctx.author.create_dm()
		dm = ctx.author.dm_channel
	if ((isAdmin(ctx.author)) and (int(size)>0)):
		update_JSON('max_file_size',size)
		refresh_config()
		await dm.send('Changed max file size to {}'.format(size))
	else:
		await dm.send('You do not have permissions to use this command!')
		print ('{} tried to use MaxFileSize command'.format(ctx.author.name))
		
@bot.command(name='MaxFilesAllowed', help='Sets maximum amount of files bot will accept for your intro sound')
async def max_file_size(ctx, size):
	global maxSoundFiles
	global data
	await ctx.message.delete()
	dm = ctx.author.dm_channel
	if dm is None:
		await ctx.author.create_dm()
		dm = ctx.author.dm_channel
	if ((isAdmin(ctx.author)) and (int(size)>1)):
		update_JSON('max_sound_files',size)
		refresh_config()
		await dm.send('Changed maximum amount of files to {}'.format(size))
	else:
		await dm.send('You do not have permissions to use this command!')
		print ('{} tried to use MaxFilesAllowed command'.format(ctx.author.name))


#List user sounds to user
@bot.command(name='MySound', help='Show user the sound files they have saved')
async def show_user_sound(ctx):
	if ((str(ctx.channel.type) == 'private') and (ctx.message.author.bot != True)):
		user = ctx.message.author.name.lower() + '#' + ctx.message.author.discriminator
		files = os.listdir(fileDir+'/sounds/'+user)
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		
		dmString = ''
		i = 1
		for sounds in files:
			dmString += '\n({}) {}'.format(i,sounds)
			i+=1
		
		await dm.send(dmString)
		
#Allows user to remove files
@bot.command(name='RemoveSound', help='Show user the sound files they have saved')
async def remove_user_sound(ctx,_file):
	if ((str(ctx.channel.type) == 'private') and (ctx.message.author.bot != True)):
		user = ctx.message.author.name.lower() + '#' + ctx.message.author.discriminator
		files = os.listdir(fileDir+'/sounds/'+user)
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		
		removed = False
		for sounds in files:
			if _file==sounds:
				os.remove(fileDir+'/sounds/'+user+'/'+_file)
				removed = True
		
		if removed:
			await dm.send('Successfully removed '+_file+'.')
		else:
			await dm.send('Failed to delete '+_file+'. Try using \'MySounds\' command to check the exact spelling.')
		

#DM the bot a .mp3 file and it will make it your intro tune!
@bot.command(name='AddSound', help='DM bot with this command and an attched .mp3 file to set your intro sound')
async def add_sound(ctx):
	global fileSizeAllowed
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		attatchments = ctx.message.attachments
		
		if ((len(attatchments)!=0) and (len(attatchments)<2)):
			if ((int(attatchments[0].size)<int(fileSizeAllowed)) and (attatchments[0].filename.endswith('.mp3'))):
				user = ctx.message.author.name.lower() + "#" + ctx.message.author.discriminator
				#check if user sound file folder exists
				if not os.path.exists(fileDir + '/sounds/' + user):
					os.makedirs(fileDir + '/sounds/' + user)
				#check how many files they currently have
				files = os.listdir(fileDir+'/sounds/'+user)
				if (len(files) < int(maxSoundFiles)):
					fileName = fileDir + '/sounds/' + user + '/' + attatchments[0].filename.lower()
					print('File {} being saved'.format(attatchments[0].filename))
					await attatchments[0].save(fileName)
					print ('saved {} to sounds folder'.format(fileName))
					await dm.send('Your intro sound number {} was saved to your folder!'.format(len(files)+1))
				else:
					await dm.send("You have too many sound files already saved! there is a limit of {} files!".format(maxSoundFiles))
					print('Failed to save due to too many files')
				
			else:
				await dm.send('I\'m sorry, I am too stupid to understand that. Please make sure you send only 1 .mp3 that is under {} bytes'.format(fileSizeAllowed))
				print('Failed to save')
		else:
			await dm.send('I\'m sorry, I am too stupid to understand that. Please make sure you send only 1 .mp3 that is under {} bytes'.format(fileSizeAllowed))
			print('Failed to save')
				
	
	await bot.process_commands(message)

		
#checks if name is in no sleep timer list, if so return True
def has_no_sleep_timer(name):
	global noSoundTimer
	global data
	refresh_config()
	for user in noSoundTimer:
		if name==user:
			return True
	return False
				
#checks if channel name is in blocked channels list and returns false if it is				
def check_channel_if_allowed(channelName):
	global clockedChannels
	refresh_config()
	
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
	
	token = data['discord_token']
	adminUsers = data['admin_user']
	cmdPrefix = data['cmd_prefix']
	soundTime = data['sound_time']
	noSoundTimer = data['no_sound_timer']
	disabledIntros = data['user_disabled_intro']
	blockedChannels = data['blocked_channels']
	fileSizeAllowed = data['max_file_size']
	maxSoundFiles = data['max_sound_files']


#for updating JSON fields and writting them to file
def update_JSON(key, newVal):
	global data
	global fileDir
	data[key] = newVal
			
	wFile = open(fileDir+'/config.json','w')
	json.dump(data,wFile,indent = 2)	
	wFile.close()
	refresh_config()

#internal function to check admin name and discriminator to admin list
def isAdmin(_author):
	global adminUsers
	disID = _author.name + "#" + _author.discriminator
	if (disID.lower() in (name.lower() for name in adminUsers)):
		return True
	else:
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

