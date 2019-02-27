#!/usr/bin/python
# TwilioServerDaemon.py 

import twilio
from twilio.rest import Client

import datetime
import time
import os
import threading
from awrManager import *
from dropbox_downloadFolder import *


# ***********************************************************
#											 VARIABLES
# ***********************************************************

VERBOSE = False
logfile_path = 'log.txt'

# ***********************************************************
#											 FUNCTIONS
# ***********************************************************

# This function sends an SMS message, wrapped in some error handling
def SendSMS(client, sMsg):
  try:
    message = client.api.account.messages.create(to="",
                                                 from_="",
                                                 body=sMsg)
  except Exception as e:
    print e
    return
    
def writeToLogfile(message):
  global logfile_path
  
  try:
    logfile = open(logfile_path, "a+")
    logfile.write(time.strftime("%d/%m/%Y - %H:%M:%S: ") + message + "\n")
    logfile.close()
  except Exception as e:
    print e
  
  return
  
def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

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
  
  # Try to connect to Twilio
  while not connected:
    try:
      client = Client(account_sid, auth_token)
      SendSMS(client, 'Twilio Server Booting up!')
      writeToLogfile('Twilio Server Booting up!')
      connected = True
      
    except Exception as e:
      print e
      
    # Wait one second before trying again
    time.sleep(1)
    
  # Setup GPIO
  lower_awr()
      
  # Once connect, run main loop once a second
  while connected:
    
    try:
    
      # Only process messages from today (Twilio uses UTC)
      message_list = client.messages.list(from_='')
        
      # If a message exists, grab the top one:
      if message_list:
      
        # if it has been received and hasn't been processed yet
        if message_list[0].status == "received" and message_list[0].body.encode('utf-8') is not "":
      
          # Save message object
          last_message = message_list[0]

          # Get text command
          message_rx = last_message.body.encode('utf-8')
          if VERBOSE: print(message_rx)
          
          # Update body to indicate message processed
          client.messages(last_message.sid).update(body="")

          # TODO: Run commands
          if "restrict" in message_rx.lower():
            message_tx = 'Moving water spout up'
            try:
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
              lower_awr()
              
              SendSMS(client, message_tx)
              writeToLogfile(message_tx)
              if VERBOSE: print(message_tx)
            except Exception as e:
              print e
              writeToLogfile('Error: ' + message_tx)
              if VERBOSE: print('Error: ' + message_tx)
          
          if "exit" in message_rx.lower():
            SendSMS(client, "Twilio Server Exiting...")
            writeToLogfile('User wants to kill program')
            return
          
          if "update" in message_rx.lower():
            message_tx = 'Attempting download from dropbox...'
            SendSMS(client, message_tx)
            writeToLogfile(message_tx)
            
            try:
              if downloadFolderToDropbox() is True:
                message_tx = 'Downloaded from dropbox...'
              else:
                message_tx = 'Download from dropbox failed.'
              
              SendSMS(client, message_tx)
              writeToLogfile(message_tx)
              if VERBOSE: print(message_tx)
            except Exception as e:
              print e
              writeToLogfile('Error: ' + message_tx)
              if VERBOSE: print('Error: ' + message_tx)
              
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

