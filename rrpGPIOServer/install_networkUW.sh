#!/bin/bash

sudo cp interfaces /etc/network/interfaces

sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

sudo service networking restart