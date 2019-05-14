#!/usr/bin/python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------------------
# Implementation of scratch Remote Sensor Protocol Client
#
# Copyright (C) 2013, 2017  Gerhard Hepp
#
# This program is free software; you can redistribute it and/or modify it under the terms of 
# the GNU General Public License as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with this program; if 
# not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, 
# MA 02110, USA 
# ---------------------------------------------------------------------------------------------
#
# This code is partially based on code from Simon Walters
# Here the original credentials:
#
#     This code is copyright Simon Walters under GPL v2
#     This code is derived from Pi-Face scratch_handler by Thomas Preston
#     This code now hosted on Github thanks to Ben Nuttall
#     Version 2.3 15Jun13
#
# Major rework done in July 2013 till 2017  by Gerhard Hepp
# Features are
# - protocol handling
# - Modularization of Software (server connection, data model, configuration, monitoring)
# - Configuration in XML for various IO-settings
# - GUI for monitoring and simulation on non-Raspberry environments 
# - added various devices
# - scratch2 support
# --------------------------------------------------------------------------------------------
# target environment:  python release 3.3, 3.6 preferred
#                      python release 2.7 will no longer be actively supported.
# --------------------------------------------------------------------------------------------
# changes:
#
 
changes = [
    ('2018-11-19', 'added MPR121 device.'),
    ('2018-11-19', 'removed perpetual scratch 1.4 connection reminder.'),
    ('2018-11-19', 'bugfix value conversion scratch2 int values and other fixes for value conversions.'),
    ('2018-11-15', 'added gps adapter for GY_GPS6MV2 provided by SFYRAKIS.'),
    ('2018-11-15', 'favicon 404 error corrected.'),
    ('2018-11-14', 'Logging config file can be defined on command line. Add NotificationHandler class.'),
    ('2018-11-11', 'Value conversion error for servo, pwm in arduino adapter fixed.'),
    ('2018-11-10', 'web application start/stop restructure to handle tornado 5.x better.'),
    ('2018-11-01', 'W1_DS1820: slight changes in log messages.'),
    #
    ('2018-04-02', 'added compatibility support for tornado release 5'),
    ('2018-02-25', 'changed scratch2 extension loader; changed some conversions in arduino_uno script'),
    ('2018-02-18', 'bugfix in javascript for adapter display.'),
    ('2018-02-17', 'config for config_camjam_edukit added (experimental, could not test'),
    ('2018-02-16', 'config tool arduinoUNO, do not allow ''undef'' as a name; scratch2Extension, special handling of ''undef'' events or names'), 
    ('2018-02-13', 'config tool for arduinoUno: remember command line file for save operation. Changed scratch2 extension to name-value pairs'), 
    ('2018-02-11', 'various experiments with scratch2 extension'), 
    ('2018-02-05', 'bugfix in scratchClientServer: scratch2 connection used orphaned dictionary which stored the name->id-relation, but was never checked for existing names'), 
    ('2018-02-04', 'added scratch2 extension installer: scratchClient/tools/scratch2connection/install.py'),
    ('2018-01-28', 'scratch2 connection: made js-code labels independent from variable names.'),
    ('2018-01-28', 'arduino uno sketch: Bugfix 0xff eeprom code'),
    ('2018-01-26', 'Bugfix: python3 bytes, bytebuffer handling corrected.'),
    ('2018-01-25', 'Bugfix: python2->3 incompatibility in arduino UNO adapter in combination with older arduino firmware.'),
    ('2018-01-24', 'Bugfix: python2->3 incompatibility in arduino UNO adapter solved.'),
    ('2018-01-22', 'Bugfix: version date now automatically matches first entry in changes.'),
    ('2018-01-07', 'Documentation, added adapter.gpio.GpioMotorPWM to configuration of adapters.'),    
    #
    ('2017-12-21', 'Bugfix: wedo adapter, Enrico Gallo reported a bug in setting tilt sensor.'),    
    ('2017-11-19', 'Bugfix: corrected error message in stepper module.'),    
    ('2017-10-17', 'dht11 based on pigpiod.'),    
    ('2017-10-11', 'pwm adapter using pigpiod.'),    
    ('2017-10-10', 'Bugfix in socket singleton again; dma_pwm bug fixes when values overflow.'),    
    ('2017-10-09', 'Bugfix in socket singleton; python3 compatibility in various modules'),    
    ('2017-10-08', 'the with-loglevel does not work; workaround increase log level on "connected" to warning'),    
    ('2017-07-17', 'bugfix HCSR04-adapter; renamed class adapter.pigpiod.HC_SR04_Adapter to adapter.pigpiodAdapter.HC_SR04_Adapter'),    
    ('2017-07-08', 'add CAP1208, add ExplorerHatPro config'),    
    ('2017-07-01', 'add description of scratch2/raspbian to web docu. Add hotkeys for java arduinoUNO config tool.'),    
    #
    ('2017-06-29', 'add configuser dir to search path in -c option'),    
    ('2017-06-20', 'arduinoUNO arduino program: handles unitialized eeprom as empty'),    
    ('2017-06-17', 'bugfix scratchClientConfig, counter-pullup not handled correctly'),    
    ('2017-06-17', 'bugfix scratchClientConfig, baud rate not set, a6,a7 analog in not generated xml'),    
    ('2017-06-16', 'gpio, pwm servo, corrected rate calculation'),    
    ('2017-06-15', 'scratch 1.4 usage hints for web page'),    
    ('2017-06-15', 'arduinoUNO adapter, ident handling added'),    
    ('2017-06-13', 'bug fixes in error messages for gpio handling in config'),    
    ('2017-06-10', 'pi2go config and adapters ADC_DAC_PCF8591 and Gpio_HCSR04_OnePin_Input'),    
    ('2017-06-04', 'major rework: logging in json, tornato replaces cherrypy, scratchx-support, bug fixes in monitoring&simulation page animation; remove gui-switches from commandline'),    
    ('2017-05-27', 'lirc IR receive adapter.'),
    ('2017-04-22', 'openweathermap api, added possibility to set location.'),
    ('2017-04-21', 'sonicpi-adapter added'),
    ('2017-04-06', 'mqtt-adapter with optional username, password'),
    ('2017-03-19', 'Minecraft-Adapter for pi, based on mcpi-library'),
    ('2017-03-16', 'Wedo2-Adapter, additional log messages., wedo2scratch script, changed two buttons in motion sensor setup.'),
    ('2017-03-13', 'added SCROLL PHAT HD-Adapter and sample scratch script'),
    ('2017-03-13', 'added MICRO DOT PHAT-Adapter'),
    ('2017-03-05', 'extensions in config file are marked with <extension>. Old files work with new code. Affects ADC_MCP3202_10_Zone_Input, UNO_Adapter, MQTT_Adapter, MCP23S17_Adapter, CommunicationAdapter, WebsocketXY_Adapter.'),    
    ('2017-03-04', 'added mqtt-adapter.'),    
    ('2017-02-27', 'arduino.ino, added counter function, changes in config tool.'),    
    ('2017-02-18', 'arduino.ino, comment changes, additional ident reset command.'),    
    ('2017-02-17', 'bugfix: wrong config file did not cause program to terminate.'),    
    ('2017-02-14', 'singleton-ipc, added; added command line switch to select singleton logic'),    
    ('2017-02-13', 'singleton-pid, redesign, changes in shutdown logic'),    
    ('2017-02-12', 'UNO_Adapter, reconnect logic reworked; arduinoUno with added "disconnect"-command'),    
    ('2017-02-10', 'config tool to edit UNO_Adapter xml config files included.'),    
    ('2017-01-26', 'minor changes in log messages on scratch connection.'),  
    ('2017-01-16', 'improved connection handling and last-value in arduinoUNO adapter.'),  
    ('2017-01-10', 'all queue definitions wrapped by a helper class to fix python2/3 compatibility.'),  
    #
    ('2016-12-19', 'arduino nano used as neopixel driver'),  
    ('2016-12-01', 'pico2wave tts adapter'),  
    ('2016-10-30', 'bugfix adapter.arduino.UNO_Adapter (usage of analog pins on arduino for digital io)'),  
    ('2016-09-26', 'optional parameters for servo adapter DMA_PWMServo'),  
    ('2016-08-19', 'added hc-sr04 sensor based on pigpiod'),           
    ('2016-08-14', 'added lego wedo2 adapter'),           
    ('2016-07-31', 'added openweathermap-api access'),
    #
    ('2016-06-05', 'added config file config_AT42QT1070'),
    ('2016-05-30', 'Adapter GpioButtonInput is deprecated, use GpioEventInput instead'),
    ('2016-05-28', 'fixed bug in GpioEventInput (inverse did not work)'),
    ('2016-05-22', 'DS1820-Adapter, added error messages'),
    ('2016-05-21', 'UNO_Adapter, for posix systems: added an exclusive lock to serial connection'),           
    ('2016-04-17', 'removed a flaw in accessing files.'),
    ('2016-03-28', 'added twitter adapter.'),
    ('2016-03-25', 'added arduino adapter for LEGO powerfunctions.'),
    ('2016-03-19', 'added support for external speech recognition adapter.linux.Linux_ASR_Adapter.'),
    ('2016-03-07', 'added aplay and arecord command adapter.'),
    ('2016-02-29', 'bugfix RPIO2 library: pwm to zero did not reliably switch off when fullscale to zero.'),
    ('2016-02-28', 'ident code for arduino sketch.'),
    ('2016-02-21', 'performance optimizations in arduinoUNO adapter and arduino sketch.'),
    ('2016-02-15', 'added servo capability for arduinoUNO-adapter, reworked reconnect policy for this adapter.'),
    ('2016-01-02', 'dma based PWM added, gpioLib-switch removed.'),
    #
    ('2015-12-09', 'bug fixes in pwm-servo; value range checks added.'),
    ('2015-11-16', 'pianoHat Adapter added.'),
    ('2015-11-16', 'bugfix in GpioInput-Adapter.'),
    ('2015-11-12', 'added blink(1)'),
    ('2015-10-16', 'modified the "is the code already started"-code; made the code relative to current python code.'),
    ('2015-10-16', 'corrected a bug in formatting an error message'),
    ('2015-09-26', 'added senseHat-adapter LED, environmental, IMU'),
    ('2015-09-25', 'added senseHat_Adapter (limited functionality, LED only)'),
    ('2015-08-29', 'reworked CommunicationAdapter, which was broken after the publish-subscibe reengineering'),
    ('2015-08-03', 'RFID-Reader adapter added'),
    ('2015-08-01', 'pico board adapter added'),
    ('2015-07-17', 'GpioValueInput-Adapter added. Allows to send predefined values on low/high'),
    ('2015-07-14', 'MCP3008'),
    ('2015-07-09', 'error recovery strategy for scratch 1.4 2015-jan-15, issue #136'),
    #
    ('2015-05-25', 'added arduinoUNO adapter.'),
    ('2015-05-23', 'system time adapter added'),
    ('2015-05-05', 'piFace support, piGlow support'),
    ('2015-05-03', 'solved display issues in GUI for multiple scratch variables into one adapter method; added PCA9865; removed bugs in MCP23S17. Refactoring the i2c-system.'),
    ('2015-04-19', 'removed bug in positioning popup editor in adapter display'),
    ('2015-04-13', 'internal: implemented plugin methods for an adapter to modify web server.'),
    ('2015-04-11', 'added DHT22 with atmega328-coprocessor; added smartphone positional sensors'),
    ('2015-04-08', 'additional configuration check: input/output names unique in config.'),
    ('2015-04-07', 'converted event publishing to pubsub pattern, web interface to websocket'),
    ('2015-03-28', 'added atmel-328 adapter for hc-sr04'),
    ('2015-03-16', 'added operation system command adapter'),
    ('2015-03-16', 'added half-bridge motor adapter'),
    ('2015-03-14', 'added MCP23S17-adapter'),
    ('2015-03-01', 'added usb adapter for HID-barcode-scanner'),
    ('2015-02-12', 'added servoblaster adapter'),
    ('2015-01-04', 'removed quote-handling-problem in broadcast name strings'),
    #
    ('2014-12-22', 'added a lookup strategy for config files which allows for simpler command line syntax'),
    ('2014-12-17', 'namevalueparser, corrected for quote in name'),           
    ('2014-12-13', 'worked on python3 compatibility; changed package structure (adapter.adapter->adapter.adapters); fixed codepage conversion problems in web access.'),           
    ('2014-11-14', 'Added DS1820 adapter.'),           
    ('2014-10-17', 'Modified help output.'),           
    ('2014-10-03', 'modified socket code, outgoing to better handle utf8 strings; modified test adapter with different data types.'),           
    ('2014-09-20', 'changed dma channel to 4'),           
    ('2014-09-01', 'Added BH1750 Luminosity Sensor, i2c bus'),           
    ('2014-08-29', 'GpioInput, fixed "inverse"-Problem.'),           
    ('2014-08-08', 'texttospeech, fixed an exception problem.'),           
    ('2014-08-03', 'renamed ADCInput to ADC_MCP3202_10_Input.'),           
    ('2014-08-01', 'bug fix for activation of adapters.'),           
    ('2014-07-30', 'renamed adapter.stepper.Stepper to adapter.stepper.BipolarStepper added adapter.stepper.UnipolarStepper'),
    ('2014-07-26', 'added \'changes\' command line switch.'),
    ('2014-07-26', 'added SIM800 GSM Modem support.'),
    ('2014-07-12', 'added GpioStateOutput, for signalling client state. Needed some  adjustments in interrupt handling to allow for this special type of adapter. '),
    #
    ('2014-06-19', 'performance optimizations adapter, commandResolve-Logic (no eval).'),
    ('2014-06-17', 'minor performance optimizations in namevalueparser.'),
    ('2014-06-12', 'corrected some instability in receiving variables.'),
    ('2014-05-01', 'changed send method to scratch, utf-8 aware and pytho3 compatible'),
    ('2014-03-31', 'fixed config file config_ikg_7segment.xml added error checks in reading xml files.'),
    ('2014-03-12', 'changed data receive logic/process dataraw to be more robust. Instantiation the managers on need only.'),
    ('2014-03-11', 'changed data receive logic to work even for very long records.'),
    ('2014-02-22', 'added I2C-Handlers for ADC ADS1015 '),
    ('2014-02-03', 'enable one broadcast/value for multiple adapters'),
    ('2014-01-24', 'fixed a conversion error from adapter to framework (now always strings)'),
    ('2014-01-06', 'added WS2801-Adapter, some bug fixes in SPI handling'),
    #
    ('2013-12-26', 'added remote connection adapter'),
    ('2013-12-01', 'configuration file for portMapping in xml'),
    ('2013-11-16', 'added sighup in order to catch terminal closed.'),
    ('2013-11-16', 'added code to enforce a singleton running instance')  
  ]

# never got the right date matching the last entry in changes history.
# hope this helps   
version = changes[0][0]

# --------------------------------------------------------------------------------------------
from array import *
import json
import sys
import protocol
import os
import os.path
import re
import signal
import socket
import traceback
import threading
import time

import server.scratchClientServer

# from adapter.adapters import GPIOAdapter
# from adapter.adapters import SPIAdapter
# from adapter.adapters import I2CAdapter

import spi.manager
import i2c.manager

    
import configuration
import errorManager
#import eventHandler
import publishSubscribe

import logging
import logging.config

import helper.abstractQueue

if sys.platform.startswith('linux'):
    import grp
    
import helper.logging
import singleton.singletonIPC
import singleton.singletonPID
import singleton.singletonNONE

commandlineHelp = """
-host <ip>           Scratch Host ip or hostname, default 127.0.0.1
-port <number>       Port number, default 42001

-c <configfile>
-config <configfile> Name of config xml-file, default config/config.xml 
                     There is a lookup strategy used: add xml extension when needed, 
                     check if file exists literally. Then try to find a matching file 
                     in configuser dir, next in config dir. Try to add 'config_' to 
                     filename also. 

-C <configfile>      Name of config xml-file, default config/config.xml 
                     There is NO lookup strategy used, only literal.

-l <logconfigfile>   Name of a log config file. Supersedes -v, -d setting.
                     Relative path or absolute file name.
                          
-gpioLib             set the gpiolibrary, default 'RPi_GPIO_GPIOManager'
                     deprecated
                     
-singletonPID        when multiple instances are running, report other instance and 
                     terminate
-singletonIPC        when multiple instances are running, terminate other instance
                     used port 42003 (default from 2017-02-14)
-singletonNONE       no singleton policy applied. For debug only

debug and test switches

-validate            Validate config and terminate.

-h
-help                print command line usage and exit
-v                   verbose logging (see also -l option)
-d                   debug logging (see also -l option)
-license             print license and exit.
-changes             print changes list  and exit.
-version             print version and exit.

"""

#
# Set some constants 
#
DEFAULT_PORT = '42001'
DEFAULT_HOST = '127.0.0.1'

DEFAULT_CONFIGFILENAME = 'config/config.xml'
DEFAULT_PORTMAPPINGFILENAME = 'config/portMapping.xml'

DEFAULT_GPIOLIB = 'RPi_GPIO_GPIOManager'

DEFAULT_PIDFILENAME = 'scratchClient.pid'

DEFAULT_SINGLETON = 'IPC'

BUFFER_SIZE = 240 #used to be 100
SOCKET_TIMEOUT = 2

verbose = False
debug = False
loggingconfigfile = None

validate = False
#
# when set to true, then the connection error message is repeated each 5 minutes or so.
#
perpetual_scratch14_connection_error = False

configFileName = DEFAULT_CONFIGFILENAME
portmappingFileName = DEFAULT_PORTMAPPINGFILENAME

host = DEFAULT_HOST
port = DEFAULT_PORT
gpioLib = DEFAULT_GPIOLIB
singletonFlag = DEFAULT_SINGLETON

pidFileName = DEFAULT_PIDFILENAME

gpl2 = """
 Copyright (C) 2013, 2018  Gerhard Hepp

 This program is free software; you can redistribute it and/or modify it under the terms of 
 the GNU General Public License as published by the Free Software Foundation; either version 2 
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
 without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 See the GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License along with this program; if 
 not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, 
 MA 02110, USA 
"""

_runIt = True

import environment        
# ================================================================================================
#
# 

class ScratchSender:
    
    def __init__(self, handler):
        self.handler = handler
        self.name = "scratchSender"
        self._stopEvent = threading.Event()
        self._lock = threading.Lock()
        
        #publishSubscribe.Pub.subscribe('scratch.output.value', self.sendValue)
        #publishSubscribe.Pub.subscribe('scratch.output.command', self.send)

    def stop(self):
        if debug:
            logger.warn("{n:s}: stop".format(n=self.name) )
        self._stopEvent.set()
        try:
            self.thread.join(1.0)
        except Exception as e:
            logger.warn("{n:s}: {m:s}".format(n=self.name, m=str(e)) )
        
    def start(self):
        if debug:
            logger.warn("{n:s}: start".format(n=self.name) )

        self.handler.subscribe(self)
        self.thread = threading.Thread( target=self.run, name=self.name)
        self._stopEvent.clear()
        self.thread.start()

    def stopped(self):
        return self._stopEvent.isSet()

    def setSocket(self, socket):
        self.scratch_socket = socket
        
    def run(self):
        pass

    
    def sendValue(self, message):
        """send a 'sensor-update'"""
        
        bcast_str = 'sensor-update "' + message['name'] + '" ' +  message['value']
        if sys.version_info.major == 2:
            if logger.isEnabledFor(logging.INFO):
                try:
                    logger.info('ScratchSender, send: {bs:s}'.format(bs= bcast_str.decode('utf-8') ) )
                except UnicodeEncodeError:
                    logger.warn("ScratchSender, send sensor-update, name {n:s} value can't be displayed to python2 unicode problems".format(n= message['name']))
        if sys.version_info.major >= 3:
            if logger.isEnabledFor(logging.INFO):
                logger.info('ScratchSender, send: {bs:s}'.format(bs= bcast_str ) )
        
        self.send_scratch(bcast_str)

    def sendCommand(self, message):
        """send a 'broadcast'"""
        bcast_str = 'broadcast "{name:s}"'.format( name= message['name'] )
        if logger.isEnabledFor(logging.INFO):
            logger.info('ScratchSender, send: {bs:s}'.format(bs= bcast_str) )
        
        self.send_scratch(bcast_str)

    def send_scratch(self, cmd):
        """this method will be used by multiple threads, so synchronizing
        looks reasonable. Missing synchronization could explain sporadic
        scratch breakdowns."""
        self._lock.acquire()
        try:
            # cmd is a str
            # in python3, use following code
            if True:
                
                if sys.version_info.major == 2:
                    try:
                        c = bytearray(cmd)
                    except TypeError as e:
                        logger.error(e)
                        c = bytearray(cmd, 'utf-8' )
                        
                    n = len( c )
                if sys.version_info.major >= 3:
                    c = bytes( cmd, 'utf-8' )
                    n = len( c )
    
                a = array('B')
                # convert len to the first four bytes
                a.append(((n >> 24) & 0xFF))
                a.append(((n >> 16) & 0xFF))
                a.append(((n >>  8) & 0xFF))
                a.append((n & 0xFF))
                
                if sys.version_info.major == 2:
                    a.extend( c )
                    # print('send a', a)
                if sys.version_info.major >= 3:
                    a.frombytes( c )
                try:
                    totalsent = 0
                    while totalsent < len(a):
                        sent = self.scratch_socket.send(a[totalsent:])
                        if sent == 0:
                            self.handler.event_disconnect()
                            # 
                            return
                        totalsent += sent
                        
                except Exception as e:
                    if logger.isEnabledFor(logging.INFO):
                        logging.info(e)
                    pass
            else:
                n = len(cmd)
                a = array('c')
                a.append(chr((n >> 24) & 0xFF))
                a.append(chr((n >> 16) & 0xFF))
                a.append(chr((n >>  8) & 0xFF))
                a.append(chr(n & 0xFF))
                
                try:
                    self.scratch_socket.send(a.tostring() + cmd)
                except Exception as e:
                    if logger.isEnabledFor(logging.INFO):
                        logging.info(e)
                    pass
        finally:
            self._lock.release()
# ================================================================================================
#
# 

class ScratchListener:
    
    def __init__(self, handler):
        self.handler = handler
        self.name ="scratchListener"
        self._stopEvent = threading.Event()
        
    def setSocket(self, socket):  
        self.scratch_socket = socket
    
    def stop(self):
        if debug:
            logger.warn("{n:s}: stop".format(n=self.name) )
        self._stopEvent.set()
        try:
            self.thread.join(1.0)
        except Exception as e:
            logger.warn("{n:s}: {m:s}".format(n=self.name, m=str(e)) )
            
    def start(self):
        if debug:
            logger.warn("{n:s}: start".format(n=self.name) )
        self._stopEvent.clear()
        self.thread = threading.Thread( target=self.run, name="scratchListener")
        self.thread.start()

    def stopped(self):
        return self._stopEvent.isSet()

    def run(self):
        """main listening routine to remote sensor protocol"""
        #print("ScratchListener thread started")
        logger.debug("scratchListener thread started")
        
        if sys.version_info.major == 2:
            # 
            # data is current, aggregated bytes received. From these, records are extracted.
            #
            data = ''
            # 
            # chunk are bytes arriving from the socket
            #
            chunk = ''
            #
            # record is a full, interpretable array of bytes. 
            #
            record = ''
            #
            while not self.stopped():
                try:
                    #
                    # get the bytes from the socket
                    # This is not necessarily a full record, just some bytes.
                    # 
                    chunk =  self.scratch_socket.recv(BUFFER_SIZE) 
                    
                    if logger.isEnabledFor( logging.DEBUG):
                        x =  map(ord, chunk)
                        s = ''
                        for xx in x:
                            s += "{xx:02x} ".format(xx=xx)
                        logger.debug("received " + s )
    
                    #
                    # no data arriving means: connection closed
                    #
                    if len(chunk) == 0:
                        self.handler.event_disconnect()
                        break
    
                    data += chunk
                    #
                    # there are multiple records possible in one 
                    # received chunk
                    # ... as well as the data could not be long enough for a full record.
                    #
                    # need at least 4 bytes to identify length of record.
                    #
                    while  len(data) >= 4:
                        #
                        # there are problems with scratch 1.4 2015-jan-15 on raspbian, not sending data according to bytes, but 
                        # length according to chars. When there are utf-8-chars in data stream, this is
                        # not the same.
                        # For this situation, an emergency recovery strategy is implemented: look for first two bytes of buffer 
                        # to be zero- it is reasonable that messages are less then 65536 bytes long.
                        if ord(data[0]) != 0 or ord(data[1]) != 0:
                            logger.error("fatal: first two bytes of message are not zero, discard data till zeros found")   
                            discard = 0
                            while len(data) > 2:
                                if ord(data[0]) == 0 and ord(data[1]) == 0:
                                    break
                                else:
                                    data = data[1:]
                                    discard += 1
                            logger.error("discarded {disc:d} bytes".format(disc=discard))
                            if not (len(data) >= 4 ):
                                break
                        # end of error stratgey
                        
                        recordLen = (ord(data[0]) << 24) +     \
                                    (ord(data[1]) << 16) +     \
                                    (ord(data[2]) <<  8) +     \
                                    (ord(data[3]) <<  0 )                
                        #            
                        if recordLen > 512:
                            logger.debug("unusual large record length received: {len:d}".format(len=recordLen))   
                        #
                        # are there enough bytes in data for a full record ?
                        # if not, leave the loop here and wait for more chunks to arrive.
                        #
                        if len(data) < 4+recordLen:
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug("not enough data in buffer, have {have:d}, need {len:d}".format(have=len(data),len=recordLen))   
                            break   
                        
                        record = data[4: 4+recordLen]
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug( 'data received from scratch-Length: %d, Data: %s' , len(record), record)
                        
                        self.processRecord ( record )
                        #
                        # cut off the record from the received data
                        #               
                        data = data[4+recordLen:]
                        #
                except socket.timeout:
                    # if logger.isEnabledFor(logging.DEBUG):
                    #    logger.debug( "No data received: socket timeout")
                    continue
                except Exception as e:
                    logger.warn(e)
                    if logger.isEnabledFor(logging.DEBUG):
                        traceback.print_exc(file=sys.stdout)
                    self.handler.event_disconnect()
                    self.stop()
                    continue
                
        if sys.version_info.major == 3:
            # 
            # data is current, aggregated bytes received. From these, records are extracted.
            #
            data = b''
            # 
            # chunk are bytes arriving from the socket
            #
            chunk = b''
            #
            # record is a full, interpretable array of bytes. 
            #
            record = ''
            #
            while not self.stopped():
                try:
                    #
                    # get the bytes from the socket
                    # This is not necessarily a full record, just some bytes.
                    # 
                    chunk =  self.scratch_socket.recv(BUFFER_SIZE) 

                    if logger.isEnabledFor( logging.DEBUG):
                        s = ''
                        for xx in chunk:
                            s += "{xx:02x} ".format(xx=xx)
                        logger.debug("received " + s )
                    
    
                    #
                    # no data arriving means: connection closed
                    #
                    if len(chunk) == 0:
                        self.handler.event_disconnect()
                        break
    
                    data += chunk
                    #
                    # there are multiple records possible in one 
                    # received chunk
                    # ... as well as the data could not be long enough for a full record.
                    #
                    # need at least 4 bytes to identify length of record.
                    #
                    while  len(data) >= 4:
                        #
                        # there are problems with scratch 1.4 2015-jan-15 on raspbian, not sending data according to bytes, but 
                        # length according to chars. When there are utf-8-chars in data stream, this is
                        # not the same.
                        # For this situation, an emergency recovery strategy is implemented: look for first two bytes of buffer 
                        # to be zero- it is reasonable that messages are less then 65536 bytes long.
                        if data[0] != 0 or data[1] != 0:
                            logger.error("fatal: first two bytes of message are not zero, discard data till zeros found")   
                            discard = 0
                            while len(data) > 2:
                                if data[0] == 0 and data[1] == 0:
                                    break
                                else:
                                    data = data[1:]
                                    discard += 1
                            logger.error("discarded {disc:d} bytes".format(disc=discard))
                            if not (len(data) >= 4 ):
                                break
                        # end of error stratgey
                        
                        recordLen = ( data[0] << 24) +     \
                                    ( data[1] << 16) +     \
                                    ( data[2] <<  8) +     \
                                    ( data[3] <<  0 )                
                        #            
                        if recordLen > 512:
                            logger.debug("unusual large record length received: {len:d}".format(len=recordLen))   
                        #
                        # are there enough bytes in data for a full record ?
                        # if not, leave the loop here and wait for more chunks to arrive.
                        #
                        if len(data) < 4+recordLen:
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug("not enough data in buffer, have {have:d}, need {len:d}".format(have=len(data),len=recordLen))   
                            break   
                        
                        data4 = data[4: 4+recordLen]
                        #print( data4)
                        record = data4.decode('utf-8') 
                        
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug( 'data received from scratch-Length: %d, Data: %s' , len(record), record)
                        
                        self.processRecord ( record )
                        #
                        # cut off the record from the received data
                        #               
                        data = data[4+recordLen: ]
                        #
                except socket.timeout:
                    # if logger.isEnabledFor(logging.DEBUG):
                    #    logger.debug( "No data received: socket timeout")
                    continue
                except Exception as e:
                    logger.warn(e)
                    if logger.isEnabledFor(logging.INFO):
                        traceback.print_exc()
                    self.handler.event_disconnect()
                    self.stop()
                    continue

        logger.debug("scratchListener thread stopped")
        
    BROADCAST = 'broadcast'
    SENSOR_UPDATE = 'sensor-update'
    LEN_BROADCAST = len(BROADCAST)
    LEN_SENSOR_UPDATE = len(SENSOR_UPDATE)
    
    def processRecord(self, dataraw):
        if  dataraw.startswith(self.BROADCAST):

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('broadcast in data: %s' , dataraw)
                
            broadcastString = dataraw[ self.LEN_BROADCAST: ]
            broadcastName = protocol.BroadcastParser(broadcastString ).parse()
            
            publishSubscribe.Pub.publish("scratch.input.command.{name:s}".format(name=broadcastName), { 'name':broadcastName } )
            # self.commandResolver.resolveBroadcast( broadcastName )
            
        elif  dataraw.startswith(self.SENSOR_UPDATE):
            #print(dataraw)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug( "sensor-update rcvd %s" , dataraw) 
            
            #
            # data are name value pairs. name always in quotes, values either quotes or not (for numeric values)
            # String quotes are handled by doubling the quotes.
            # 
            nameValueString = dataraw[ self.LEN_SENSOR_UPDATE: ]
            # print("parse ", nameValueString)
            nameValueArray = protocol.NameValueParser(nameValueString ).parse()
            # print(nameValueArray)
            # for nv in nameValueArray:
            #    print("single nv = ", nv)
            for nv in nameValueArray:
                # print("process single nv = ", nv)
                # import pdb; pdb.set_trace()
                if logger.isEnabledFor(logging.INFO):
                    logger.info('sensor-update: {name:s}, {value:s}'.format(name=nv[0], value=nv[1]) )
                    
                publishSubscribe.Pub.publish("scratch.input.value.{name:s}".format(name=nv[0]), { 'name':nv[0], 'value':nv[1] } )
            # self.commandResolver.resolveValue(nv[0], nv[1])            
        else:
            logger.warn("unknown command in received data " + dataraw )
# ================================================================================================
#
# 
    
class ThreadManager:
    """the threads are collected here in order to have one point to terminate each of them"""
    
    def __init__(self):
        self.threads = []
        self.socketThreads = []
        
    def append_thread(self, t):
        self.threads.append(t)
            
    def append_socket(self, t):
        self.socketThreads.append(t)    

    def cleanup_socket(self):
        
        logger.debug("ThreadManager, cleanup_socket")

        for thread in self.socketThreads:
            logger.debug("cleanup_socket: stop thread %s", str(thread.name ))
            thread.stop()
    
        for thread in self.socketThreads:
            logger.debug("cleanup_socket: wait join %s", str(thread.name ))
            try:
                thread.join(1)
                if thread.isAlive():
                    logger.debug("cleanup_socket: wait join %s timeout",  thread.name) 
                else:
                    logger.debug("cleanup_socket: wait join %s ok",  thread.name)
            except Exception as e:
                logger.warn("cleanup_socket: wait join %s: %s", thread.name, str(e))

        
    def cleanup_thread(self):
        
        logger.warn("ThreadManager, cleanup_thread")
        
        for thread in self.threads:
            logger.debug("cleanup_threads: stop thread '%s'", str(thread))
            thread.stop()
    
        for thread in self.threads:
            logger.debug("cleanup_threads: wait join '%s'", thread)
            try:
                thread.join(1)
                if thread.isAlive():
                    logger.debug("cleanup_threads: wait join '%s' timeout",  thread.name) 
                else:
                    logger.debug("cleanup_threads: wait join '%s' ok",  thread.name)
            except Exception as e:
                logger.warn("cleanup_threads: wait join '%s': %s", thread.name, str(e))
            

## threadManager = ThreadManager()
# ================================================================================================
#
# 

class ScratchClientApplication:
    """Manage Application, receive start/stop from handlers for scratch14 and scratch2. Start/Stop adapters.
       And handle Configuration. last not least"""
    
    SHUTDOWN = 'shutdown'
    STATE_CONNECTED = 'connected'
    STATE_DISCONNECTED = 'disconnected'
       
    def __init__(self, eventQueue):
        self.name = "ScratchClientApplication"
        self.thread = threading.Thread( target = self.run, name="ScratchClientApplication")
        self._stopEvent = threading.Event()

        self.eventQueue = eventQueue
        self.state = None
        
        self.handlers = []
        
        #TODO self.listener = None
        #TODO self.sender = ScratchSender()
        #self.commandResolver = CommandResolver()    
        self.gpioManager = None
        self.managers = []   
        
        self.gui = server.scratchClientServer.ServerThread( parent = self )
        environment.append('gui',  self.gui )
       
        # read config files
        configuration.allEverGpios = configuration.GPIORegistry(modulePathHandler.getScratchClientBaseRelativePath(portmappingFileName) )   
        
        self.config = configuration.ConfigManager(configFileName)
        self.config.configure()

        if errorManager.hasErrors() :
            logger.error("Errors: %s", str(errorManager.errors ))
            logger.error("There are errors in configuration file '{f:s}'".format(f=configFileName))
            self.shutdown()
            return
        
        self.config.check()
        
        if errorManager.hasErrors() :
            logger.error("Errors: %s", str(errorManager.errors ))
            logger.error("There are errors in configuration file '{f:s}'".format(f=configFileName))
            self.shutdown()
            return
        
        if errorManager.hasWarnings() :
            logger.warn("Warning: %s", str(errorManager.warnings ))

        if validate:
            logger.warn("Validating, exit with no errors.")
            self.shutdown()
            return
        # 
        self.gui.start()
        #threadManager.append_thread(self.gui)
        # -----------------
        #
        # Instantiate the managers for the various hardware resources
        #
        needGPIO = False
        needSPI = False
        needI2C = False
        needDMA = False
        
        for module in self.config.getAdapters():
            adapterMethods = configuration.AdapterMethods (module)

            if adapterMethods.hasMethod('setGpioManager'):
                needGPIO = True
            
            if adapterMethods.hasMethod('setSPIManager'):
                needSPI = True

            if adapterMethods.hasMethod('setI2CManager'):
                needI2C = True
            
            if adapterMethods.hasMethod('setDMAManager'):
                needDMA = True
        
        if needGPIO:
            self.gpioManager = configuration.GPIOManager( lib=gpioLib )
            self.managers.append(self.gpioManager)
            # forceSimulation = self.gpioManager.getSimulation()
    
        if needSPI:
            self.spiManager = spi.manager.SPIManager()
            self.managers.append(self.spiManager)
        
        if needI2C:
            self.i2cManager = i2c.manager.I2CManager()
            self.managers.append(self.i2cManager)

        if needDMA:
            import dma.manager
            self.dmaManager = dma.manager.DMAManager()
            self.managers.append(self.dmaManager)
        # -----------------
        for m in self.managers:
            m.setActive(True)
        # -----------------        
        # Assign the managers for hardware resources to the adapters.
        # There are adapters needing more than one manager.
        #
        # the code here ensures that the various adapter types 
        # use only one instance ofs the managers
        # could be solved by static methods and singleton instances,
        # but I could not find a solution for this.
        #
        
        for module in self.config.getAdapters():
            adapterMethods = configuration.AdapterMethods (module)

            if adapterMethods.hasMethod('setGpioManager'):
                module.setGpioManager(self.gpioManager)
            
            if adapterMethods.hasMethod('setSPIManager'):
                module.setSPIManager(self.spiManager)
            
            if adapterMethods.hasMethod('setI2CManager'):
                module.setI2CManager(self.i2cManager)
            
            if adapterMethods.hasMethod('setDMAManager'):
                module.setDMAManager(self.dmaManager)
            
        # -----------------------------------------------
        
        # removed SIGKILL     
        signals = (
            "SIGINT", 
            "SIGTERM", 
            # "SIGHUP"
                   )    
        for sig in signals:
            try:
                # on windows, not all signals available
                s = eval("signal." + sig)
                signal.signal(s, self.sigHandler)
            except AttributeError as e:
                logger.warning('AttributeError: setting signals {signal:s}: {exception:s} '.format(signal=sig, exception=str(e) ) )
                pass
            except RuntimeError as e:
                logger.debug('RuntimeError: setting signals {signal:s}: {exception:s} '.format(signal=sig, exception=str(e) ) )
                pass
            
    def setActive(self, name, state):
        for adapter in self.config.getAdapters(): 
            adapter.setActive(state)
            
    def registerHandler (self, aHandler):
        self.handlers.append( aHandler)
        
    def start(self):
        if debug:
            logger.warn("{n:s}: start".format(n=self.name) )
        self.thread.start()
        for handler in self.handlers:
            handler.start()
        
    def getName(self):
        return self.name
    
    def subscribe(self, sender):
        self.config.configureCommandResolver( sender )
        
    def unsubscribe(self, sender):
        self.config.unconfigureCommandResolver( sender )
        
    def stop(self):
        self._stopEvent.set()

    def stopped(self):
        return self._stopEvent.isSet()
        
    def run(self):
        logger.debug("%s thread started", self.getName() )

        while not(self.stopped()):
            s = ''
            try:
                s = self.eventQueue.get(True, 0.1)
            except helper.abstractQueue.AbstractQueue.Empty:
                continue
            
            if s == 'disconnect':
                #print("disconnect received")
                self._disconnect()
            if s == 'connect':
                #print("connect received")
                self._connect()
            if s == ScratchClientApplication.SHUTDOWN:
                self.shutdown()
                
        logger.warn("%s thread terminated", self.getName() )
        
    def event_disconnect(self):
        self.eventQueue.put('disconnect')
    
    def event_connect(self):
        #print("event connect")
        self.eventQueue.put('connect')
        
    def _disconnect(self):    
        logger.info("{n:s}: event_disconnect".format(n=self.name))
        if self.state == self.STATE_CONNECTED:
            if verbose:
                print ("Scratch disconnected")

            logger.info("{n:s}: set adapters inactive".format(n=self.name))
            for module in self.config.getAdapters():
                module.setActive(False)
            # self.gpioManager.setActive(False)
            # threadManager.cleanup_socket()
            self.state = self.STATE_DISCONNECTED
            self.event_connect()
        else:
            if debug:
                print(self.name, "not in a state to disconnect", self.state)
            logger.info("{n:s}: set adapters inactive".format(n=self.name))
            for module in self.config.getAdapters():
                module.setActive(False)
                
                
        self.state = self.STATE_DISCONNECTED
                    
    def _connect(self):
        logger.info("event_connect")
        
        if self.state == self.STATE_DISCONNECTED:
            #
            for module in self.config.getAdapters():
                module.setActive(True)
            #print("listener starting")
             
            if logger.isEnabledFor(logging.INFO):
                logger.info ("Running....")
            # self.sender.start()
        else:
            if debug:
                print(self.name, "not in a state to connect", self.state)
            for module in self.config.getAdapters():
                module.setActive(True)
         
        self.state = self.STATE_CONNECTED

    def shutdown(self):
        logger.warn("shutdown sequence started")

        for adapter in self.config.getAdapters():
            #
            # kindly ask the adapters to terminate
            #
            if adapter.isActive():
                adapter.setActive(False)
            #    
            # stop those adapters not bound to active/inactive    
            # TODO: let the adapters register automatically on thread manager.
            adapter.stop()

        for m in self.managers:
            m.setActive(False)
            
        for handler in self.handlers:
            handler.stop()
        logger.warn("shutdown adapters, managers, handlers stopped")
        
        self.gui.stop()
        self.stop()
        #
        # the own thread is included in 'cleanup_threads
        # self.stop()
        global _runIt
        _runIt = False
       
    def sigHandler(self, signum, frame):
        logger.warn("received signal {sig:s}".format(sig= str(signum)))
        self.eventQueue.put( ScratchClientApplication.SHUTDOWN)
    
class ClientHandler:
    def start(self):
        raise Exception("must be overridden")
        
    def getName(self):
        raise Exception("must be overridden")
    
    def subscribe(self, sender):
        self.manager.subscribe( sender)
        
    def unsubscribe(self, sender):
        self.manager.unsubscribe( sender)
            
    def stop(self):
        raise Exception("must be overridden")

    def event_disconnect(self):
        raise Exception("must be overridden")
    
    def event_connect(self):
        raise Exception("must be overridden")
 
class ScratchClientHandler( ClientHandler):
    """manage connection to scratch_1_4"""
        
    STATE_START = 0
    STATE_CONNECTED = 1
    STATE_DISCONNECTED = 2
    
    state = STATE_DISCONNECTED
    
    myQueue = None
    managers = None
    
    def __init__(self, manager):  
        self.name="scratchClientHandler"
        self.manager = manager 
        # import pdb; pdb.set_trace() 
        #global forceSimulation 
        self.thread = threading.Thread( target=self.run, name="scratchClientHandler")
        self._stopEvent = threading.Event()

        self.myQueue = helper.abstractQueue.AbstractQueue()

        self.listener = ScratchListener(self)
        self.sender = ScratchSender(self)
        #self.commandResolver = CommandResolver()    

    def start(self):
        if debug:
            logger.warn("{n:s}: start".format(n=self.name) )
        self.thread.start()
        self.myQueue.put('connect')
        
    def getName(self):
        return self.name
    
    def subscribe(self, sender):
        self.manager.subscribe( sender)
            
    def stop(self):
        self._stopEvent.set()

        self.listener.stop()
        self.sender.stop()
        
    def stopped(self):
        return self._stopEvent.isSet()
        
    def run(self):
        logger.debug("%s thread started", self.getName() )

        while not(self.stopped()):
            s = ''
            try:
                s = self.myQueue.get(True, 0.1)
            except helper.abstractQueue.AbstractQueue.Empty:
                continue
            if s == 'disconnect':
                #print("disconnect received")
                self._disconnect()
            if s == 'connect':
                #print("connect received")
                self._connect()
            if s == 'shutdown':
                self.shutdown()
                
        logger.warn("%s thread terminated", self.getName() )
        
    def event_disconnect(self):
        self.myQueue.put('disconnect')
    
    def event_connect(self):
        #print("event connect")
        self.myQueue.put('connect')
        
    def _disconnect(self):    
        logger.info("event_disconnect")
        if self.state == self.STATE_CONNECTED:
            if verbose:
                print ("Scratch disconnected")

            logger.info("set adapters inactive")
            self.manager.event_disconnect()
            
            self.listener.stop()
            self.sender.stop()
            
            # self.gpioManager.setActive(False)
            #threadManager.cleanup_socket()
            self.state = self.STATE_DISCONNECTED
            self.event_connect()
            
    def _connect(self):
        logger.info("event_connect")
        if self.state == self.STATE_DISCONNECTED:
            # open the socket
            if debug:
                logger.debug( 'Starting to connect...')
            the_socket = self.create_socket(host, port)
            
            if the_socket == None:
                # print("no socket")
                logger.error("no socket")
                return
            
            if self.stopped():
                return
            
            with helper.logging.LoggingContext(logger, level=logging.INFO):
                #TODO setting the log level does not work (with json config?)
                # so set level to warn
                logger.info('Connected to Scratch !')
            
            the_socket.settimeout(SOCKET_TIMEOUT)

            self.listener.setSocket(the_socket)
            self.sender.setSocket(the_socket)
            
            # threadManager.append_socket(self.listener)
            #threadManager.append_socket(sender)
            #
            self.manager.setActive(self.name, True)
            #print("listener starting")
            
            if logger.isEnabledFor(logging.INFO):
                logger.info ("Running....")
                
            self.sender.start()
            self.listener.start()
            # self.sender.start()
         
            self.state = self.STATE_CONNECTED
                   
    
    def create_socket(self, host, port):
        scratch_sock = None
        # count is used to limit the number of log messages on console
        count = 0

        while not( self.stopped() ):
            try:
                if count == 0:
                    logger.info( 'Trying to connect to scratch.' )
                
                scratch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                scratch_sock.settimeout(0.15)
                scratch_sock.connect((host, int(port)))
                break
            
            except socket.error:
                scratch_sock = None
                if count == 0:
                    with helper.logging.LoggingContext(logger, level=logging.INFO):
                        logger.info( "There was an error connecting to Scratch 1.4 !" )
                        # in german for the kids in school:
                        logger.info( "  Unterstuetzung fuer Netzwerksensoren einschalten!" )
                        logger.info( "  Activate remote sensor connections!" )
                        logger.info( "  No Mesh session at host: %s, port: %s" , host, port) 
                
                for _ in range(0,100):
                    if self.stopped():
                        break
                    time.sleep(0.075)
                
                count += 1
                # when count is reset, the message is repeated
                if perpetual_scratch14_connection_error:
                    count %= 40
        return scratch_sock
        
# ================================================================================================
#
# 
class ModulePathHandler:
    modulePath = None
    moduleDir = None
    
    def __init__(self):
        _cwd = os.getcwd()
        _file = __file__
        
        if sys.platform == "linux" or sys.platform == "linux2":
            # linux
            self.modulePath = _cwd + '/' + _file
            self.moduleDir =  os.path.split(self.modulePath)[0]
            
        elif sys.platform == "darwin":
            # MAC OS X
            self.modulePath = _cwd + '/' + _file
            self.moduleDir =  os.path.split(self.modulePath)[0]
            
        elif sys.platform == "win32":
            # Windows
            self.modulePath = _file
            self.moduleDir =  os.path.split(self.modulePath)[0]
            
        
    def getModulePath(self):
        return self.modulePath
    
    def getModuleDir(self):
        return self.moduleDir
    #
    # specific methods for scratchClient
    #
    def getScratchClientBaseDir(self):
        return os.path.join( sys.path[0], '..')
    
    def getScratchClientBaseRelativePath(self, relPath):
        return os.path.normpath( 
                                os.path.join( self.getScratchClientBaseDir(), relPath )
                                )
# ================================================================================================
#
# 
        
modulePathHandler = ModulePathHandler()
logger = None
    
if __name__ == '__main__':
    
    configLookupStrategy = True
    
    try:
        i = 1
        while i <  len (sys.argv):
            if '-host' == sys.argv[i]:
                host = sys.argv[i+1]
                i += 1
                
            elif '-port' == sys.argv[i]:
                port = sys.argv[i+1]
                i += 1
            
            elif ( '-config' == sys.argv[i] ) or ( '-c' == sys.argv[i] ):
                configLookupStrategy = True
                configFileName = sys.argv[i+1]
                i += 1
            
            elif ( '-C' == sys.argv[i] ):
                configLookupStrategy = False
                configFileName = sys.argv[i+1]
                i += 1
                
            elif ( '-l' == sys.argv[i] ):
                loggingconfigfile = sys.argv[i+1]
                i += 1
                  
            elif '-gpioLib' == sys.argv[i]:
                print('gpioLib is deprecated, ignored')
                # gpioLib = sys.argv[i+1]
                i += 1
            
            elif '-v' == sys.argv[i]:
                verbose = True
            
            elif '-d' == sys.argv[i]:
                debug = True
            
            elif '-help' == sys.argv[i]:
                print(commandlineHelp)
                sys.exit(1)
            elif '-h' == sys.argv[i]:
                print(commandlineHelp)
                sys.exit(1)
            
            elif '-license' == sys.argv[i]:
                print(gpl2)
                sys.exit(1)
            
            elif '-changes' == sys.argv[i]:
                for x in changes:
                    print(x[0] + " " + x[1])
                sys.exit(1)
            elif '-version' == sys.argv[i]:
                print('scratchClient ' + version)
                sys.exit(1)

            elif '-validate' == sys.argv[i]:
                validate = True
                
            elif '-singletonIPC' == sys.argv[i]:
                singletonFlag = 'IPC' 
            elif '-singletonPID' == sys.argv[i]:
                singletonFlag = 'PID' 
            elif '-singletonNONE' == sys.argv[i]:
                singletonFlag = 'NONE' 
                
              
            else:
                print("Command line error, unknown switch", sys.argv[i])    
            i += 1
                                   
    except Exception:
        print(commandlineHelp)
        sys.exit(1)
    
    # ------ Logging configuration -----------
    lcf = False
    if loggingconfigfile == None:
        lcf = False
    elif os.path.isfile ( loggingconfigfile):
        lcf = True
    else:
        lcf = False
    
    lFile = '' 
    if lcf :
        lFile = loggingconfigfile   
    elif debug == True:
        lFile = 'logging/logging_debug.json'
    elif verbose == True:
        lFile = 'logging/logging_verbose.json'
    else:        
        lFile = 'logging/logging.json'
    
    # print(modulePathHandler.getScratchClientBaseRelativePath(lFile))
    if os.path.isfile(lFile ):
        llFile = lFile
    else:
        llFile = modulePathHandler.getScratchClientBaseRelativePath(lFile)
    
    try:     
        # read a json file and strip off comments 
        # as comments are line-related, read file line by line
        jsonText = ''
        
        fi = open(llFile)
        while True:
            line = fi.readline()
            if '' == line:
                break
            line = line.rstrip('\n')
            line = re.sub(r'^[ \t]*//.*$', '', line)
            line = re.sub(r'^[ \t]*#.*$', '', line)
            jsonText += line + '\n'
        fi.close()
        
        logging_dict = json.loads(jsonText)
        logging.config.dictConfig(logging_dict )
        
        jsonText = None
        line = None
        
    except Exception as e:
        print("Could not load log config file ", llFile)
        print(e)
        logging.basicConfig()
    # ----------------------------------------
        
    logger = logging.getLogger(__name__)
    
    if sys.version_info.major == 2:
        with helper.logging.LoggingContext(logger, level=logging.INFO):
            logger.info('Consider using python3 to execute this program !')

    logging.debug("create ScratchClient")
    # ----------------------------------------------------------
    # look for config files
    #
    cFileFound = False
    cFile = configFileName
    
    if configLookupStrategy:
        #
        # add '.xml' if not available
        #
        if not (cFile.endswith( '.xml' )):
            cFile += '.xml'
            logger.debug("LookupStrategy config file: add xml extension")
        #
        # take it literally
        #
        if not( cFileFound):
            pathConfigFile = modulePathHandler.getScratchClientBaseRelativePath( cFile )
            cFileFound = os.path.isfile( pathConfigFile )

        for preferredDir in [ 'configuser/', 'config/']:
            #
            #
            if not( cFileFound):
                pathConfigFile =  modulePathHandler.getScratchClientBaseRelativePath( preferredDir + cFile )
                cFileFound = os.path.isfile( pathConfigFile )
                if cFileFound:
                    logger.info("LookupStrategy config file found: "+ pathConfigFile)
            
            #
            # look in ../ dir
            #
            if not( cFileFound):
                pathConfigFile =  modulePathHandler.getScratchClientBaseRelativePath( '../' + preferredDir + cFile )
                cFileFound = os.path.isfile( pathConfigFile )
                if cFileFound:
                    logger.info("LookupStrategy config file found: "+ pathConfigFile)
            #
            # check if a 'config_'-prefix is missing. Do this only when no path is given.
            #
            if cFile.find('/') < 0:
                if not( configFileName.startswith('config_')):
         
                    if not( cFileFound):
                        pathConfigFile = modulePathHandler.getScratchClientBaseRelativePath('config_' + cFile)
                        cFileFound = os.path.isfile( pathConfigFile ) 
                        if cFileFound:
                            logger.debug("LookupStrategy config file: add prefix 'config_'")   
                            logger.info("LookupStrategy config file found: "+ pathConfigFile)
                        
                    if not( cFileFound):
                        pathConfigFile =  modulePathHandler.getScratchClientBaseRelativePath( preferredDir + 'config_' + cFile )
                        cFileFound = os.path.isfile( pathConfigFile )
                        if cFileFound:
                            logger.debug("LookupStrategy config file: add prefix 'config_'") 
                            logger.info("LookupStrategy config file found: "+ pathConfigFile)
                        
                    if not( cFileFound):
                        pathConfigFile =  modulePathHandler.getScratchClientBaseRelativePath('../' + preferredDir + 'config_' + cFile)
                        cFileFound = os.path.isfile( pathConfigFile )
                        if cFileFound:
                            logger.debug("LookupStrategyconfig file: add prefix 'config_'") 
                            logger.info("LookupStrategyconfig file found: "+ pathConfigFile)
    
        #
        # if not found, go back to what was defined on command line.
        #
        if cFileFound:
            configFileName = pathConfigFile
        else:
            configFileName = cFile
    # ----------------------------------------------------------
    singletonInstance = None
    if singletonFlag == 'PID':
        singletonInstance = singleton.singletonPID.SingletonPID( modulePathHandler, DEFAULT_PIDFILENAME )
    if singletonFlag == 'IPC':
        singletonInstance = singleton.singletonIPC.SingletonIPC( port=42003 )
    if singletonFlag == 'NONE':
        singletonInstance = singleton.singletonNONE.SingletonNONE( )
        
    singletonInstance.start()
    
    logging.info("start scratch client for scratch1.4 and scratchX, {v:s}".format(v=version) )
    logger.debug("sys.path    = {p:s}".format(p=str(sys.path)) )

    
    eventQueue_ScratchClientApplication = helper.abstractQueue.AbstractQueue()
    
    scratchClientApplication  = ScratchClientApplication(eventQueue_ScratchClientApplication)
    
    scratchClientHandler = ScratchClientHandler( scratchClientApplication )
    scratchClientApplication.registerHandler( scratchClientHandler )
    
    scratchXHandler = server.scratchClientServer.ScratchXHandler( scratchClientApplication )
    scratchClientApplication.registerHandler( scratchXHandler )

    scratchClientApplication.start()

    
    singletonInstance.registerShutdown( scratchClientApplication)
    
    nWTR = 1
    while _runIt:
        if nWTR % 20000 == 0:
            logger.debug("scratchClient still running")
        time.sleep(0.1)
        nWTR += 1
    
    singletonInstance.stop ()
    # for debugging purpose, list out not yet terminated threads.
    # MainThread counts as 1, so list only if activeCount > 1
    # 
    cnt = 0    
    while (cnt < 2 ) and threading.activeCount() > 1:
        cnt += 1
        for t in threading.enumerate():
            logger.warning("active threads: " + t.name )
        time.sleep(2)
    
    print("scratchClient terminated")
    logger.debug("scratchClient terminated")
    
    os._exit(0)
