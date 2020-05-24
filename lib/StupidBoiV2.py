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
					#choose a random sound from their sound folder to play
					files = os.listdir(cfg.soundsPath+'/'+user)
					song = random.choice(files)
					bot.voice_clients[vcVal].play(discord.FFmpegPCMAudio(cfg.soundsPath+'/'+user+'/'+song))
					cfg.Log('Playing {}\'s intro sound: {}'.format(member.name,song))
					
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
#THESE ARE DM COMMANDS
#Allows users to add a sound to their account 
#DM the bot a .mp3 file and it will make it your intro tune. 
@bot.command(name='AddSound', help='DM bot with this command and an attched .mp3 file to set your intro sound')
async def add_sound(ctx):
	cfg.fileSizeAllowed
	#Check if the message is a DM
	if ((str(ctx.channel.type) == 'private') and (ctx.author.bot != True)):
		dm = ctx.author.dm_channel
		if dm is None:
			await ctx.author.create_dm()
			dm = ctx.author.dm_channel
			
		#Grab the message attachments
		attatchments = ctx.message.attachments
		
		#if there is less than the max sound files allowed
		if ((len(attatchments)!=0) and (len(attatchments)<int(cfg.maxSoundFiles))):
			#if the attatchment is within the allowed file size and is a .mp3
			if ((int(attatchments[0].size)<int(cfg.fileSizeAllowed)) and (attatchments[0].filename.endswith('.mp3'))):
			
				user = str(ctx.message.author.id)
				
				#check if user sound file folder exists, if not make one
				if not os.path.exists(cfg.soundsPath+'/'+ user):
					os.makedirs(cfg.soundsPath+'/'+ user)
					
				#check how many files they currently have
				files = os.listdir(cfg.soundsPath+'/'+user)
				
				#work through each attachment
				for song in attatchments:
					#check if user is allowed more files
					if (len(files) < int(cfg.maxSoundFiles)):
						fileName = cfg.soundsPath+'/' + user + '/' + song.filename.lower()
						cfg.Log('{}\'s file {} being saved'.format(user,song.filename))
						await song.save(fileName)
						cfg.Log('saved {} to {}\'s sound folder'.format(song.filename,user))
						await dm.send('Your intro sound number {} was saved to your folder!'.format(len(files)+1))
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



