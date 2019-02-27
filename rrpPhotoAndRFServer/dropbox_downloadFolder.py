#!/usr/bin/python
# uploadFileToDropbox.py 

import dropbox
import os

#Varibles
VERBOSE = False

#Insert auth token from dropbox account
auth_token = ''

def downloadFolderToDropbox():
  try:
    # Connect to Dropbox
    dbx = dropbox.Dropbox(auth_token)
    accnt = dbx.users_get_current_account()

    if VERBOSE: print 'Linked Account: ', accnt.name.display_name
             
    # Download example folder "folder"
    folder_metadata = dbx.files_list_folder('/folder')
    #if VERBOSE: print 'metadata: ', folder_metadata
        
    for file_metadata in folder_metadata.entries:              
      try:
        if VERBOSE: print file_metadata
        
        filepath = file_metadata.path_display
        filename = file_metadata.name
        if VERBOSE: print 'Attempted Download: ' + filepath

        # Download File from Dropbox
        metadata, response = dbx.files_download(filepath)
        out = open(filename, 'wb')
        out.write(response.content)
        out.close()
         
        if VERBOSE: print 'Downloaded: ' + filename

      except:
        print 'ERROR: File ' + filename + ' Download: ' + sys.exc_info()[0]

    print 'Folder Download: Complete'
    return True

  except:
    print 'ERROR: Folder Download: ' + sys.exc_info()[0]
    return False

if __name__ == "__main__":
  VERBOSE = True
  downloadFolderToDropbox()

