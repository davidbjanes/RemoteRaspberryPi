from twilio.rest import Client
 
# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = ""
auth_token = ""

# API Keys
#sid_token = ""
#secret_token  = ""

client = Client(account_sid, auth_token) 
 
client.messages.create(
    to = "", 
    from_ = "", 
    body = "Test from RRPServer: Hello World!", 
    media_url = "http://farm2.static.flickr.com/1075/1404618563_3ed9a44a3a.jpg", 
)

print message.sid
