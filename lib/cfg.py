# cfg
# Globalized things needed throughout all modules

from datetime import datetime
import os
from os.path import dirname
import sys

#Variables modified by JSONReader
token = ''
adminUsers = []
cmdPrefix = ''
soundTime = ''
noSoundTimer = []
disabledIntros = []
blockedChannels = []
fileSizeAllowed = ''
maxSoundFiles = ''

#current directory path
fileDir = os.getcwd()
configPath = dirname(fileDir)+'/config.json'
soundsPath = dirname(fileDir)+'/sounds'


#Basic logging function to timestamp output
#Might be expanded to write to a log file
def Log(_logString):
	logString = _logString
	now = datetime.now()
	currentTime = now.strftime("%m/%d/%Y %H:%M:%S")

	print(currentTime+': '+logString)
	
	