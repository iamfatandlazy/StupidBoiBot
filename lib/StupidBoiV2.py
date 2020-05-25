# StupidBoiV2
# Author: IAmFatAndLazy


import cfg
import JSONreader

import sys
import os
import random

#Discord.py specific 
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import asyncio


#read in variables from config file
JSONreader.ReadConfig(cfg.configPath)

#setup bot to start
bot = commands.Bot(command_prefix=cfg.cmdPrefix)

cfg.Log('IAmFatAndLazy\'s StupidBoiV2 is launching...')


#############################################################
#Command calls here
#This keeps this file readable and easier to expand on


#Called when the bot starts/connects to Discord
@bot.event
async def on_ready():
	cfg.Log('Checking for sounds folder.')
	#Check to see if sounds folder exists
	if (os.path.exists(cfg.soundsPath)):
		cfg.Log('Sounds folder found!')
	else:
		try:
			#Try to make the sounds folder if it does not exist
			os.mkdir(cfg.soundsPath)
			cfg.Log('No sounds folder found so one was created.')
		except:
			#If folder creation fails, alert the user and exit.
			cfg.Log('Failed to create sounds folder. Please make one yourself and restart the bot.')
			sys.exit(0)
			
	cfg.Log('{} has connected to Discord!'.format(bot.user))
	
	await bot.change_presence(activity=discord.Game(name='$help'))



#Plays sound from sounds folder when user joins approved voice channel
#If user has more than one intro saved it will be choosen randomly
@bot.event
async def on_voice_state_update(member,before,after):
	#if the bot is not leaving a channel, is not currently playing a sound and the user is not a bot continue
	if ((after.channel is not None)and(len(bot.voice_clients)==0)and(member.bot==False)):
		
		#read variables from JSON in case of changes
		JSONreader.ReadConfig(cfg.configPath)
		
		#get user unique id
		user = str(member.id)
		
		#old way of making usernames easier to read, deprecated as a risk of users changing discriminator
		#user = member.name.lower()+'#'+member.discriminator 
		
		#If moving to a NEW voice channel, the bot is allowed in the channel, and the user who triggered has not disabled their intro
		if ((before.channel!=after.channel)and(after.channel.name not in cfg.blockedChannels)and(user not in cfg.disabledIntros)):
			#if the user has a sounds folder with sound files in it
			if ((os.path.exists(cfg.soundsPath+'/'+user))and(len(os.listdir(cfg.soundsPath+'/'+user))>0)):
			
				currentChannel=after.channel
				#Wait to connect to users voice channel
				await currentChannel.connect()
				
				#find where the user is
				vcVal = 0
				for i, vc in enumerate(bot.voice_clients):
					if vc.guild==member.guild:
						vcVal = i
						
				#check if the bot is already playing anything
				if not bot.voice_clients[vcVal].is_playing():
					try:
						#choose a random sound from their sound folder to play
						files = os.listdir(cfg.soundsPath+'/'+user)
						song = random.choice(files)
						bot.voice_clients[vcVal].play(discord.FFmpegPCMAudio(cfg.soundsPath+'/'+user+'/'+song))
						cfg.Log('Playing {}\'s intro sound: {}'.format(member.name,song))
					except Exception as e:
						cfg.Log('Failled to play {}\'s intro sound:{}'.format(member.name,e))
						
					#timer to allowe limited time for audio to play
					timer = 0
					enabledTimer = True
					
					#if the user is found in the noSoundTimer list disabled their timer
					if user in cfg.noSoundTimer:
						enabledTimer = False
						
					while (bot.voice_clients[vcVal].is_playing()and(timer<=int(cfg.soundTime))):
						await asyncio.sleep(1)
						if enabledTimer==True:
							timer+=1
							
					#Bot disconnects from voice channel
					await bot.voice_clients[vcVal].disconnect()		
		

		
################################################################
#ALL CHANNEL ACTIVATED COMMANDS
#checks if bot is playing sound, then stops it
@bot.command(name='Silence', help='Silences the bot if it is currently playing audio')
async def silence_bot(ctx):
	vcVal = 0
	await ctx.message.delete()
	for i, vc in enumerate(bot.voice_clients):
		if vc.guild==ctx.guild:
			vcVal = i
	if bot.voice_clients[vcVal].is_playing():
		bot.voice_clients[vcVal].stop()
		cfg.Log(ctx.message.author.name+' silenced bot')



################################################################
#THESE ARE DM COMMANDS




#Personal user settings section
###############################
#add/remove user from disabled intro's list, 		
@bot.command(name='Intro', help='Toggles your intro sound on/off')
async def intro_toggle(ctx):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)

		#Get user ID
		user = str(ctx.author.id)
		
		#if user has disabled intro, enable it
		if user in cfg.disabledIntros:
			cfg.disabledIntros.remove(user)
			await dm.send('You have enabled your intro song(s).')
			cfg.Log(user+' has enabled their intro sound.')
		#if user has an enabled sound, disable it
		else:
			cfg.disabledIntros.append(user)
			await dm.send('You have disabled your intro song(s).')
			cfg.Log(user+' has disabled their intro sound.')
			
		#Write changes to config file	
		JSONreader.WriteToConfig(cfg.configPath,'user_disabled_intro',cfg.disabledIntros)


#Admin only commands
###############################
#if admin uses command, will add user to bot admin list		
@bot.command(name='AddAdmin', help='(Admin) Add another admin user. Uses account DiscordID NOT Username!')
async def add_admin(ctx, _userID):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				

	#If the user who used the command is an admin and the userID he presented is not already in the adminUsers file
	if (str(ctx.message.author.id) in cfg.adminUsers)and(_userID not in cfg.adminUsers):
		cfg.adminUsers.append(_userID)
		#Write new admin to the config file
		JSONreader.WriteToConfig(cfg.configPath,"admin_user",cfg.adminUsers)
		cfg.Log('{} added {} to admin list'.format(ctx.message.author.name,_userID))
		await dm.send('{} has been added to the admin list.'.format(_userID))
	else:
		#If the userID is already and admin alert the user
		if _userID in cfg.adminUsers:
			await dm.send('{} is already an admin.'.format(_userID))
		#Otherwise the user must not be an admin, as so alert them of this and log the attempt
		else:
			await dm.send('You do not have permissions to use this command!')
			cfg.Log('{} tried to add {} as an admin but was denied access.'.format(ctx.message.author.name, _userID))


#if admin uses command, will remove user from admin list		
@bot.command(name='RemoveAdmin', help='(Admin) Remove another admin user')
async def remove_admin(ctx, _userID):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				

	#If the user who used the command is an admin and the userID he presented is not already in the adminUsers file
	if (str(ctx.message.author.id) in cfg.adminUsers)and(_userID in cfg.adminUsers):
		cfg.adminUsers.remove(_userID)
		#Write new admin to the config file
		JSONreader.WriteToConfig(cfg.configPath,"admin_user",cfg.adminUsers)
		cfg.Log('{} removed {} to admin list'.format(ctx.message.author.name,_userID))
		await dm.send('{} has been removed from the admin list.'.format(_userID))
	else:
		#If the userID is already and admin alert the user
		if _userID not in cfg.adminUsers:
			await dm.send('{} is not an admin.'.format(_userID))
		#Otherwise the user must not be an admin, as so alert them of this and log the attempt
		else:
			await dm.send('You do not have permissions to use this command!')
			cfg.Log('{} tried to remove {} as an admin but was denied access.'.format(ctx.message.author.name, _userID))
			

#Lists all admin users along with their UserID for easy management/removal
@bot.command(name='ListAdmins', help='(Admin) View the list of admins')
async def list_admins(ctx):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
	if (str(ctx.message.author.id) in cfg.adminUsers):
		stringBld = 'Admin users:\n\n'
		for id in cfg.adminUsers:
			stringBld +='<@!'+id+'> ID:'+id+'\n'
		
		await dm.send(stringBld)


#Default: Lists channels the bot is not allowed to enter. with optional parameter adding/removing the channel from the list
@bot.command(name='BlockedChannels', help='(Admin) Lists channels the bot is currently blocked from entering. Add a channel name after the command to add/remove a channel from this list.')
async def blocked_channels(ctx, channel=None):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
				
	if str(ctx.message.author.id) in cfg.adminUsers:
		#if channel name is passed to command
		if channel is not None:
		
			#if the channels in the list remove it
			if channel in cfg.blockedChannels:
				cfg.blockedChannels.remove(channel)
				JSONreader.WriteToConfig(cfg.configPath,'blocked_channels',cfg.blockedChannels)
				
				await dm.send('Removed {} from blocked channels list'.format(channel))
				cfg.Log('{} removed {} from blocked channels list'.format(ctx.message.author.name,channel))
				
			#if the channel is not in the list add it	
			else:
				cfg.blockedChannels.append(channel)
				JSONreader.WriteToConfig(cfg.configPath,'blocked_channels',cfg.blockedChannels)
				await dm.send('Added {} to blocked channels list'.format(channel))
				cfg.Log('{} added {} to blocked channels list'.format(ctx.message.author.name,channel))
				
		#if no argument passed to command		
		else:
			tmpString = ''
			for entry in cfg.blockedChannels:
				tmpString = tmpString + '{}\n'.format(entry)
			await dm.send('Blocked channels:\n\n{}'.format(tmpString))
		
	else:
		await dm.send('You do not have permissions to use this command!')
		cfg.Log('{} tried to use BlockedChannels command'.format(ctx.author.name))


#Allows admin users to set what the max file size of sound files is allowed		
@bot.command(name='MaxFileSize', help='(Admin) Sets maximum file size bot will accept for sound files')
async def max_file_size(ctx, size):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
	#If invoker is an admin user and the file size is more than 0			
	if (str(ctx.author.id) in cfg.adminUsers) and (int(size)>0):
		
		cfg.fileSizeAllowed = size
		JSONreader.WriteToConfig(cfg.configPath,'max_file_size',cfg.fileSizeAllowed)
		await dm.send('Changed max file size to {} bytes'.format(cfg.fileSizeAllowed))
		cfg.Log('{} changed the max file size to {} bytes'.format(ctx.author.name,cfg.fileSizeAllowed))
		
	else:
		await dm.send('You do not have permissions to use this command!')
		cfg.Log('{} tried to use MaxFileSize command'.format(ctx.author.name))

#Allows admin users to set the max amount of sound files users can have saved
@bot.command(name='MaxFilesAllowed', help='(Admin) Sets maximum amount of files bot will allow users to have at once')
async def max_files_allowed(ctx, size):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
				
	if (str(ctx.author.id) in cfg.adminUsers) and (int(size)>1):
		cfg.maxSoundFiles = size
		JSONreader.WriteToConfig(cfg.configPath,'max_sound_files',cfg.maxSoundFiles)
		await dm.send('Changed maximum amount of files to {}'.format(cfg.maxSoundFiles))
		cfg.Log('{} changed the max amount of files to {}'.format(ctx.author.name,cfg.maxSoundFiles))
	else:
		await dm.send('You do not have permissions to use this command!')
		cfg.Log('{} tried to use MaxFilesAllowed command'.format(ctx.author.name))	


#Allow admin users to disabled the sound timer for specific users. 
#Bot will play these users sound clips in full!
@bot.command(name='ToggleSoundTimer', help='(Admin) Toggles a users max time limit on their sound files')
async def toggle_sound_timer(ctx, _userID):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
	#If command caller is an admin continue			
	if (str(ctx.author.id) in cfg.adminUsers):
		#if user is in no time limit list, remove them
		if str(_userID) in cfg.noSoundTimer:
			cfg.noSoundTimer.remove(_userID)
			await dm.send('Enabled {}\'s sound timer'.format('<@!'+_userID+'>'))
			cfg.Log('{} Enabled {}\'s sound timer'.format(ctx.author.name,'<@!'+_userID+'>'))
		
		#if user not in the list, add them to it
		else:
			cfg.noSoundTimer.append(_userID)
			await dm.send('Disabled {}\'s sound timer'.format('<@!'+_userID+'>'))
			cfg.Log('{} Disabled {}\'s sound timer'.format(ctx.author.name,'<@!'+_userID+'>'))
		
		JSONreader.WriteToConfig(cfg.configPath,'no_sound_timer',cfg.noSoundTimer)
	else:
		await dm.send('You do not have permissions to use this command!')
		cfg.Log('{} tried to use ToggleSoundTimer command'.format(ctx.author.name))	

#Debugging/upgrade commands for admins
###########		
#Allow admin users to re-load config file manually
@bot.command(name='ReloadConfig', help='(Admin) Reloads configuration file manually')
async def reload_config(ctx):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
				
	if (str(ctx.author.id) in cfg.adminUsers):
		JSONreader.ReadConfig(configPath)
	else:
		await dm.send('You do not have permissions to use this command!')
		cfg.Log('{} tried to use ReloadConfig command'.format(ctx.author.name))		
		

#Updates sound folder names to support new naming scheme from V1
@bot.command(name='Migrate', help='(Admin) Migrates all users sound folders to new naming scheme')
async def migrate(ctx):
	#Check if message is a dm
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
				
	userid = str(ctx.author.id)
	
	#if user is an admin
	if (userid in cfg.adminUsers):
		#get sound folders
		folders = os.listdir(cfg.soundsPath)
		tempStr = ''
		for folder in folders:
			#split folder name 
			uID = ''
			try:
				splitName = folder.split('#')
				uID = str(discord.utils.get(bot.get_all_members(), name=splitName[0], discriminator=splitName[1]).id)
				print(splitName)
				print(uID)
			except Exception as e:
				cfg.Log('{} failed to parse during migrate. This probably means it was not a valid username'.format(folder))
			if uID!='':
				try:
					os.rename(cfg.soundsPath+'/'+folder,cfg.soundsPath+'/'+userid)
					tempStr+=folder+' --> '+userid+'\n'
				except Exception as e:
					cfg.Log('Failed to rename {}\'s folder:{}'.format(username,e))
		await dm.send('The following folders have been migrated successfully:\n\n'+tempStr)
		cfg.Log('{} Migrated the following folder successfully:\n\n{}'.format(ctx.author.name,tempStr))
	else:
		await dm.send('You do not have permissions to use this command!')
		cfg.Log('{} tried to use ReloadConfig command'.format(ctx.author.name))	

		
#Sound modifications section
###############################
#Allows users to add a sound to their account 
#DM the bot a .mp3 file and it will make it your intro tune. 
@bot.command(name='AddSound', help='Attach a .mp3 file with this command as a comment to add it to your sounds folder')
async def add_sound(ctx):
	#Check if the message is a DM
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			try:
				await ctx.author.create_dm()
				dm = ctx.author.dm_channel
			except Exception as e:
				cfg.Log('Error opening DM channel:'+e)
				
		#Grab the message attachments
		attatchments = ctx.message.attachments
		
		#if there is less than the max sound files allowed
		if ((len(attatchments)!=0) and (len(attatchments)<int(cfg.maxSoundFiles))):
			
			user = str(ctx.message.author.id)
				
			#check if user sound file folder exists, if not make one
			if not os.path.exists(cfg.soundsPath+'/'+ user):
				try:
					os.makedirs(cfg.soundsPath+'/'+ user)
				except Exception as e:
					cfg.Log('Error making user sound folder:'+e)
						
			#check how many files they currently have
			files = os.listdir(cfg.soundsPath+'/'+user)
				
			#work through each attachment
			for song in attatchments:
				#check if file is within allowd size and is an mp3
				if (int(song.size)<int(cfg.fileSizeAllowed)) and (song.filename.endswith('.mp3')):
					#check if user is allowed more files
					if (len(files) < int(cfg.maxSoundFiles)):
						try:
							fileName = cfg.soundsPath+'/' + user + '/' + song.filename.lower()
							cfg.Log('{}\'s file {} being saved'.format(user,song.filename))
							await song.save(fileName)
							cfg.Log('saved {} to {}\'s sound folder'.format(song.filename,user))
							await dm.send('Your intro sound number {} was saved to your folder!'.format(len(files)+1))
						except Exception as e:
							cfg.Log('Error saving sound:'+e)
							
					else:
						await dm.send("You have too many sound files already saved! there is a limit of {} files!".format(cfg.maxSoundFiles))
						cfg.Log('Failed to save due to too many files')
				
		else:
			await dm.send('Please make sure you send only .mp3 files that are under {} bytes'.format(cfg.fileSizeAllowed))
			print('Failed to save')


#DM the bot to remove a file from their account
#Allows user to remove files
@bot.command(name='RemoveSound', help='Use in conjunction with MySound to delete some of your sound files. Accepts the filename or index of the sound to be deleted.')
async def remove_user_sound(ctx,_file):
	if ((str(ctx.channel.type) == 'private') and (ctx.message.author.bot != True)):
		user = str(ctx.message.author.id)
		files = os.listdir(cfg.soundsPath+'/'+user)
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
		
		removed = False
		for id, sounds in enumerate(files, start=0):
			#if the filename matches delete it
			if _file==sounds:
				os.remove(cfg.soundsPath+'/'+user+'/'+_file)
				cfg.Log(user+' removed file:'+_file)
				await dm.send('Successfully removed sound file: '+_file+'.')
				removed = True
				
			#if the ID of the element matches delete it	
			elif _file==str(id):
				os.remove(cfg.soundsPath+'/'+user+'/'+files[id])
				cfg.Log(user+' removed file:'+files[id])
				await dm.send('Successfully removed sound file: '+files[id]+'.')
				removed = True
		
			
		if not removed:
			await dm.send('Failed to delete sound file: '+_file+'. Try using the\'MySounds\' command to check the exact spelling or ID.')
			cfg.Log(user+' failed to remove a sound file.')


#List user sounds to user
@bot.command(name='MySounds', help='Show your indexed sound files')
async def show_user_sound(ctx):
	if ((str(ctx.channel.type) == 'private') and (ctx.message.author.bot != True)):
		user = str(ctx.message.author.id)
		files = os.listdir(cfg.soundsPath+'/'+user)
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
			
		
		dmString = ''
		i = 0
		for sounds in files:
			dmString += '\n({}) {}'.format(i,sounds)
			i+=1
		
		await dm.send(dmString)




#############################################################
#starts the bot, dont touch this
bot.run(cfg.token)



