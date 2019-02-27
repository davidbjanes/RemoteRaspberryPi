#!/usr/bin/python
# takeUSBPhoto.py

import sys
import time
import pygame
import pygame.camera
from pygame.locals import *

VERBOSE = True

def takeUSBPhoto():

   try: 
      # INITIALIZE CAMERA
      if VERBOSE: print "Initializing..."
      pygame.init()
      pygame.camera.init()
      camlist = pygame.camera.list_cameras()
      cam = pygame.camera.Camera("/dev/video0", (640,480))
      cam.start()

      # RUN PROGRAM
      if VERBOSE: print "Taking Image..."
      img = cam.get_image()

      if VERBOSE: print "Saving Image..."
      pygame.image.save(img, 'photo.jpeg')

      cam.stop()

      print "USBPhoto: Success"
      return True

   except:
      print "USBPhoto: ERROR"
      print sys.exc_info()[0]
      return False

if __name__ == "__main__":
   takeUSBPhoto()
