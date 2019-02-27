#!/bin/bash

sudo apt-get install -y wiringpi
sudo apt-get install -y python -pip
sudo pip install wiringpi

gpio -g mode 18 pwm

gpio pwm-ms
gpio pwmc 192
gpio pwmr 2000


