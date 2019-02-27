#!/bin/bash

cp twilioServer.service /lib/systemd/system/twilioServer.service

chmod 644 /lib/systemd/system/twilioServer.service

systemctl daemon-reload
systemctl enable twilioServer.service