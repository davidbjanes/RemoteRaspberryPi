#!/usr/bin/python
# runTwilioServer.py
# server address: http://24.22.141.64:5000
# twilio default address: https://demo.twilio.com/welcome/sms/reply/

import twilio
from twilio.rest import TwilioRestClient

import MySQLdb
import datetime
import time
import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from contextlib import closing
from subprocess import call

from why import * 
from uploadFileToDropbox import *
from takeUSBPhoto import *

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#                       VARIABLES
#           CHANGE THESE TO YOUR OWN SETTINGS!
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = ""
auth_token = ""
sTwilioNumber = ""

# Gmail information - for informing homeowner that garage activity happened
recipients = ['myemail@gmail.com', 'home_owner_email@gmail.com']
sGmailAddress = ""
sGmailLogin = ""
sGmailPassword = ""

# API Keys
#sid_token = ""
#secret_token  = ""

sLastCommand = "Startup sequence initiated at {0}.  No open requests, yet".format(time.strftime("%x %X"))
sAuthorized = ""
sSid = ""
sSMSSender = ""

# Unfortunately, you can't delete SMS messages from Twilio's list.  
# So we store previously processed SIDs into the database.
lstSids = list()
iSID_Count = 0

lstAuthorized = list() # authorized phone numbers, that can open the garage
lstAuthorized.append("")
lstAuthorized.append("")
lstAuthorized.append("")
iAuthorizedUser_Count = 3

# Create MYSQL Database if it doesn't exist
# connect(host, user, password, database)
db1 = MySQLdb.connect('localhost', 'root', 'password') 
cursor = db1.cursor()
sql = 'CREATE DATABASE IF NOT EXISTS SMSLog'
cursor.execute(sql)
db1.close()

# Connect to local MySQL database
con = MySQLdb.connect('localhost', 'root', 'password', 'SMSLog')

# Connect to Twilio Server
TwilioClient = TwilioRestClient(account_sid, auth_token) 

# Dropbox Img Link
img_url = ""


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#                       FUNCTIONS
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# This function sends an SMS message, wrapped in some error handling
def SendSMS(sMsg):
  try:
    sms = TwilioClient.messages.create(
	body="{0}".format(sMsg),
	to="{0}".format(sSMSSender),
	from_="{0}".format(sTwilioNumber)
    )
  except twilio.TwilioRestException as e:
    print e
    pass
  except:
    print "Error inside function SendSMS"
    pass

# This function sends an MMS message, wrapped in some error handling
def SendMMS(sMsg):
  try:
    mms = TwilioClient.messages.create(
        body="{0}".format(sMsg),
        to="{0}".format(sSMSSender),
        from_="{0}".format(sTwilioNumber),
        media_url=img_url)
  except twilio.TwilioRestException as e:
    print e
    pass
  except:
    print "Error inside function SendMMS"
    pass

# Email the home owner with any status updates
def SendGmailToHomeOwner(sMsg):
  try:
    connect = server = smtplib.SMTP('smtp.gmail.com:587')
    starttls = server.starttls()
    login = server.login(sGmailLogin,sGmailPassword)
    msg = MIMEMultipart()
    msg['Subject'] = "GARAGE: {0}".format(sMsg)
    msg['From'] = sGmailAddress
    msg['To'] = ", ".join(recipients)
    sendit = server.sendmail(sGmailAddress, recipients, msg.as_string())
    server.quit()
  except:
    print "Error inside function SendGmailToHomeOwner"
    pass


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#                             SETUP 
#
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

try:
  # Store authorized phone numbers in a List, so we don't waste SQL resources repeatedly querying tables
  with closing(con.cursor()) as authorized_cursor:
    authorized_users = authorized_cursor.execute("select sPhone from Authorized")   
    auth_rows = authorized_cursor.fetchall()
    for auth_row in auth_rows:
      for auth_col in auth_row:
        iAuthorizedUser_Count = iAuthorizedUser_Count + 1
        lstAuthorized.append(auth_col)

  # Store previous Twilio SMS SID ID's in a List, again, so we don't waste SQL resources repeatedly querying tables
  with closing(con.cursor()) as sid_cursor:
    sid_rows = sid_cursor.execute("select sSid from TWILIO_SMS_ID")   
    sid_rows = sid_cursor.fetchall()
    for sid_row in sid_rows:
      for sid_col in sid_row:
        iSID_Count = iSID_Count + 1
        lstSids.append(sid_col)
        
  print "{0} Service loaded, found {1} authorized users, {2} previous SMS messages".format(time.strftime("%x %X"),iAuthorizedUser_Count,iSID_Count)
  #SendGmailToHomeOwner("{0} Service loaded, found {1} authorized users, {2} previous SMS messages".format(time.strftime("%x %X"),iAuthorizedUser_Count,iSID_Count))

except:
  print "{0} Error while loading service, bailing!".format(time.strftime("%x %X"))
  if con: con.close() # Not critical since we're bailing, but let's be nice to MySQL
  exit(2)


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#                            MAIN LOOP
#
#         Continuously scan Twilio's incoming SMS list
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

while (True):
  
  # The TRY block is critical.  If we cannot connect to the database, then we could possibly open the garage dozens of times.
  # If we can't contact Twilio, again, we could open the garage excessively.  Ideally, if any error at all occurs, we need
  # to completely bail, and ideally contact the home owner that this application stopped working.
  try:

    # Only process messages from today (Twilio uses UTC)
    messages = TwilioClient.messages.list(date_sent=datetime.datetime.utcnow())

    for p in messages:
      sSMSSender = p.from_

      # Only processed fully received messages, otherwise we get duplicates
      if p.status == "received":
        if p.sid not in lstSids: # Is it a unique SMS SID ID from Twilio's list?
          # Insert this new SID ID into database and List, to avoid double processing
          lstSids.append(p.sid)
          try:
            with closing(con.cursor()) as insert_sid_cursor:
              insert_sid_cursor = insert_sid_cursor.execute("insert into TWILIO_SMS_ID(sSid) values('{0}')".format(p.sid))
              con.commit()
          except:
            print "Error while inserting SID record to database"
            pass
          
          # Is this phone number authorized to open garage door?
          if p.from_ in lstAuthorized:
	    sms_body = p.body.lower()
            print "{0} Received message '{2}' from phone number {1}".format(time.strftime("%x %X"), sSMSSender, sms_body)
	 
            if sms_body == "kill":
              print "KILL'ing process... now."
              SendSMS("Received KILL command from you.  Bailing to terminal now!")
              #SendGmailToHomeOwner("Received KILL command from phone number {0}.  Exiting application!".format(sSMSSender))
              exit(3)

            if sms_body == "hi":
              SendSMS("Hi back!")
              #SendGmailToHomeOwner("Received STOP command from phone number {0}.  Send START to restart".format(sSMSSender))

            if sms_body == "why":
              SendSMS(why())
              #SendGmailToHomeOwner("Received STOP command from phone number {0}.  Send START to restart".format(sSMSSender)

            if sms_body == 'pic':
              print "Taking Photo..."
              if not takeUSBPhoto():
                SendSMS("Photo Error")

              elif not uploadPhotoToDropbox():
                SendSMS("Dropbox Upload Error")
              
              else:
                print "Uploading Photo..."
                uploadPhotoToDropbox()
                print "Sending MMS to {0}".format(sSMSSender)
  	        SendMMS("Surveilance IMG at {0}".format(time.strftime("%x %X")))
                #SendGmailToHomeOwner("Received START command from phone number {0}.  Service is now enabled".format(sSMSSender))

            if "led" in sms_body:
              led_number = sms_body[3]
              switch = sms_body[4:]
              
              if led_number == "1" and switch == "on":    code = "5510451"
              elif led_number == "1" and switch == "off": code = "5510460"
              elif led_number == "2" and switch == "on":  code = "5510595"
              elif led_number == "2" and switch == "off": code = "5510604"
              elif led_number == "3" and switch == "on":  code = "5510915"
              elif led_number == "3" and switch == "off": code = "5510924"
              elif led_number == "4" and switch == "on":  code = "5512451"
              elif led_number == "4" and switch == "off": code = "5512460"
              elif led_number == "5" and switch == "on":  code = "5518595"
              elif led_number == "5" and switch == "off": code = "5518604"
              else: code = "12345"

              try: 
                call(["sudo", "./../Timleland/rfoutlet/RFSource/codesend", code])
                SendSMS("Switch: " + led_number + " is: " + switch)
              except: 
                print "Error with RF Transmitter"
                SendSMS("Error with RF Transmitter")
              #SendGmailToHomeOwner("Received STOP command from phone number {0$

            if "ledall" in sms_body:
              switch = sms_body[6:]
              for led_number in range(1,5):
              
                if led_number == 1 and switch == "on":    code = "5510451"
                elif led_number == 1 and switch == "off": code = "5510460"
                elif led_number == 2 and switch == "on":  code = "5510595"
                elif led_number == 2 and switch == "off": code = "5510604"
                elif led_number == 3 and switch == "on":  code = "5510915"
                elif led_number == 3 and switch == "off": code = "5510924"
                elif led_number == 4 and switch == "on":  code = "5512451"
                elif led_number == 4 and switch == "off": code = "5512460"
                elif led_number == 5 and switch == "on":  code = "5518595"
                elif led_number == 5 and switch == "off": code = "5518604"
                else: code = "12345"

                try:
                  call(["sudo", "./../Timleland/rfoutlet/RFSource/codesend", code])
                except:
                  print "Error with RF Transmitter"
                  SendSMS("Error with RF Transmitter")

              SendSMS("All Switches " + switch + "!")
              #SendGmailToHomeOwner("Received STOP command from phone number {0$

          # This phone number is not authorized.  Report possible intrusion to home owner
          else:
            print "{0} Unauthorized user tried to access system: {1}".format(time.strftime("%x %X"), sSMSSender)
            #SendGmailToHomeOwner("Unauthorized phone tried opening garage: {0}".format(sSMSSender))
            print "{0} Email sent to home owner".format(time.strftime("%x %X"))

  except KeyboardInterrupt:
    exit(4)
    #SendGmailToHomeOwner("Application closed via keyboard interrupt (somebody closed the app)")
    #GPIO.cleanup() # clean up GPIO on CTRL+C exit  

  #except:
  #  print "Unable to connect to Twilio Server at {0}".format(time.strftime("%x %X")

#GPIO.cleanup()
