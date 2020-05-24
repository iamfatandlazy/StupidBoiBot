# JSONreader
# Used to read in JSON files and update global variables


from datetime import datetime
import os
import sys
import json

import cfg

#Reads the config file passed to it and updates variables 
def ReadConfig(_filePath):
	
	#config file path
	filePath = _filePath
	
	#attempt load the json
	try:
		file = open(filePath)
		data = json.load(file)
		
		#Vars to be searched for and set
		cfg.token = data['discord_token']
		cfg.adminUsers = data['admin_user']
		cfg.cmdPrefix = data['cmd_prefix']
		cfg.soundTime = data['sound_time']
		cfg.noSoundTimer = data['no_sound_timer']
		cfg.disabledIntros = data['user_disabled_intro']
		cfg.blockedChannels = data['blocked_channels']
		cfg.fileSizeAllowed = data['max_file_size']
		cfg.maxSoundFiles = data['max_sound_files']
		
		file.close()
		
	except Exception as e:
		cfg.Log('Failed to open config file!')
		cfg.Log('ERROR:'+e)
	

#Writes new values to key received
def WriteToConfig(_filePath, _key, _newVal):
	filePath = _filePath
	key = _key
	newVal = _key
	
	try:
		file = open(filePath)
		data = json.load(file)
		
		#set the JSON var as the newVal
		data[key] = newVal
			
		#open the config file to write to it	
		wFile = open(filePath,'w')
		#write the json value
		json.dump(data,wFile,indent = 2)	
		wFile.close()
	
		#Refresh the data in the variables
		ReadConfig(filePath)
	
	except Exception as e:
		cfg.Log('Failed to write to the config file!')
		cfg.Log('ERROR:'+e)