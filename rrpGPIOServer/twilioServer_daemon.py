#!/usr/bin/python
# TwilioServerDaemon.py 

import twilio
from twilio.rest import Client

import datetime
import time
import os
import threading
import platform
import re
from dropbox_downloadFolder import *

# ***********************************************************
#											 VARIABLES
# ***********************************************************

VERBOSE = False
logfile_path = 'log.txt'

RUNNING_ON_PI = False

if 'posix' in platform.system():
  from awrManager import *
  RUNNING_ON_PI = True

# ***********************************************************
#											 FUNCTIONS
# ***********************************************************

# This function sends an SMS message, wrapped in some error handling
def SendSMS(client, sMsg):

  tx_message = 'Twilio Server: ' + getSerial(6) + ' ' + sMsg
  
  try:
    message = client.api.account.messages.create(to="",
                                                 from_="",
                                                 body=tx_message)
  except Exception as e:
    print e
    return
    
def writeToLogfile(message):
  global logfile_path
  
  tx_message = 'Twilio Server: ' + getSerial(6) + ' ' + message
  
  try:
    logfile = open(logfile_path, "a+")
    logfile.write(time.strftime("%d/%m/%Y - %H:%M:%S: ") + tx_message + "\n")
    logfile.close()
  except Exception as e:
    print e
  
  return
  
def getSerial(num):
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR00000000000"

  return cpuserial[16-num:16]

def TwilioServerDaemon():
  global logfile_path
  
  # Your Account SID from twilio.com/console
  account_sid = ""
  # Your Auth Token from twilio.com/console
  auth_token  = ""
    
  connected = False
  
  
  # Setup Log file
  fullpath = os.path.realpath(__file__)
  fulldir = os.path.split(fullpath)
  fulldir = fulldir[0]
  logfile_path = os.path.join(fulldir, logfile_path)
  
  # Wait until network is connected
  time.sleep(20)
    
  # Setup GPIO
  if RUNNING_ON_PI:
    lower_awr()
	
  # Try to connect to Twilio
  while not connected:
    try:
      client = Client(account_sid, auth_token)
      SendSMS(client, 'Booting up!')
      writeToLogfile('Booting up!')
      connected = True
      
    except Exception as e:
      print e
      
    # Wait one second before trying again
    time.sleep(1)
      
  # Once connect, run main loop once a second
  while connected:
    
    try:
    
      # Only process messages from 
      message_list = client.messages.list(from_='')
        
      # If a message exists, grab the top one:
      for message in message_list:
      
        # if it has been received and hasn't been processed yet
        if message.status == "received" and message.body.encode('utf-8') is not "":
      
          # Save message object
          last_message = message

          # Get text command
          message_rx = last_message.body.encode('utf-8')
          if VERBOSE: print(message_rx)
          
          # If addressed to current client
          if getSerial(6) in message_rx.lower():
            if VERBOSE: print('Processing Message: /"' + message_rx)
          
            # Delete to indicate message processed
            client.messages(last_message.sid).delete()

            # TODO: Run commands
            if "restrict" in message_rx.lower():
              message_tx = 'Moving water spout up'
              try:
                if RUNNING_ON_PI: 
                  raise_awr()
                
                SendSMS(client, message_tx)
                writeToLogfile(message_tx)
                if VERBOSE: print(message_tx)
              except Exception as e:
                print e
                writeToLogfile('Error: ' + message_tx)
                if VERBOSE: print('Error: ' + message_tx)

            if "give" in message_rx.lower():
              message_tx = 'Moving water spout down'
              try: 
                if RUNNING_ON_PI: 
                  lower_awr()
                
                SendSMS(client, message_tx)
                writeToLogfile(message_tx)
                if VERBOSE: print(message_tx)
              except Exception as e:
                print e
                writeToLogfile('Error: ' + message_tx)
                if VERBOSE: print('Error: ' + message_tx)
            
            if "exit" in message_rx.lower():
              SendSMS(client, "Exiting...")
              writeToLogfile('User wants to kill program')
              return
            
            if "update" in message_rx.lower():
              message_tx = 'Attempting download from dropbox...'
              SendSMS(client, message_tx)
              writeToLogfile(message_tx)
              
              try:
                if downloadFolderToDropbox() is True:
                  message_tx = 'Downloaded from dropbox.'
                else:
                  message_tx = 'Download from dropbox failed.'
                
                SendSMS(client, message_tx)
                writeToLogfile(message_tx)
                if VERBOSE: print(message_tx)
              except Exception as e:
                print e
                writeToLogfile('Error: ' + message_tx)
                if VERBOSE: print('Error: ' + message_tx)
                
          # If no serial number addressed to any client
          elif [] == re.findall(r'(\d{6})', message_rx.lower()):
            
            message_tx = 'ADDR Not Found. Deleting Message: /"' + message_rx
            if VERBOSE: print(message_tx)
            
            # Delete to indicate message processed
            client.messages(last_message.sid).delete()
            
            SendSMS(client, message_tx)
            writeToLogfile(message_tx)
            if VERBOSE: print(message_tx)
                
            # For each other message
            #for message in message_list: 
            #  print(message.body.encode('utf-8'))
        
      # Wait one second before trying again
      time.sleep(1)
      
    except Exception as e:
      print e
  
  return  


if __name__ == "__main__":
   VERBOSE = True
   TwilioServerDaemon()

