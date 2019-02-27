#!/usr/bin/python
# uploadFileToDropbox.py 

import dropbox
import os
import sys
import datetime
import time

#Varibles
VERBOSE = False

# Insert auth token from dropbox
auth_token = ''

def uploadFolderToDropbox():
  try:
    # Connect to Dropbox
    dbx = dropbox.Dropbox(auth_token)
    accnt = dbx.users_get_current_account()

    if VERBOSE: print 'Linked Account: ', accnt.name.display_name
      
    for file in os.listdir('./'):
                   
      try:
        
        filename = file
        f = open(file, 'rb')
        mtime = os.path.getmtime(filename)
        data = f.read()
		
		# Upload to folder "folder"
        filepath = '/folder/' + filename
        mode = dropbox.files.WriteMode.overwrite
        
        response = dbx.files_upload(data, filepath, mode)
        
        f.close()
        if VERBOSE: print 'Uploaded: ', filename

      except:
        print 'ERROR: File ' + filename + ' Upload: ', sys.exc_info()[0]

    print 'Folder Upload: Complete'
    return True

  except:
    print 'ERROR: Folder Upload: ', sys.exc_info()[0]
    return False

if __name__ == "__main__":
  VERBOSE = True
  uploadFolderToDropbox()