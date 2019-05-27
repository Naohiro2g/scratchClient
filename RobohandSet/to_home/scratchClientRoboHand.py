#!/usr/bin/env python3
import os
import glob

ROBOHAND_TEMPLATE = "/home/pi/Documents/Scratch Projects/ROBOHAND_template.sb"

sleep = 5
os.system("scratch --document \"%s\" & sleep %d" % (ROBOHAND_TEMPLATE, sleep))
os.system("python3 /home/pi/scratchClient/src/scratchClient.py -c /home/pi/scratchClient/config/config_PCA9685.xml")
