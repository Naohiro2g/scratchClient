# -*- coding: utf-8 -*-
    # --------------------------------------------------------------------------------------------
    # Copyright (C) 2016  Gerhard Hepp
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

import adapter

try:
    import pigpio
except ImportError:
    exit("This library requires pigpio\nInstall with: sudo apt-get install pigpio")
    
import time

import logging
import helper.logging

logger = logging.getLogger(__name__)

debug = False

class HC_SR04_Error(Exception):
    NO_CONNECTION = 'no connection'
    ECHO_PIN_HIGH = 'echo pin is high'
    NO_RESPONSE = 'no response'
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

class HC_SR04():
    
    def __init__(self, trigger, echo):
        self.pi = pigpio.pi()
        if self.pi == None:
            raise HC_SR04_Error(HC_SR04_Error.NO_CONNECTION)
        
        self.trigger = trigger
        self.echo = echo
        
        self._high_tick = None
        
        self.pi.set_mode(echo, pigpio.INPUT)
        self.pi.set_pull_up_down(echo, pigpio.PUD_DOWN)
        self.pi.set_mode(trigger, pigpio.OUTPUT)
        
        self.pi.write ( trigger, 0)
        self.state = 0
        self.cnt = 0

        self._cb = self.pi.callback(echo, pigpio.EITHER_EDGE, self._cbf)
        self.mCount = 0
        
    def stop(self):
        self._cb.cancel()
        self.pi.set_mode(self.echo, pigpio.INPUT)
        self.pi.set_pull_up_down(self.echo, pigpio.PUD_DOWN)

        self.pi.set_mode(self.trigger, pigpio.INPUT)
        self.pi.set_pull_up_down(self.trigger, pigpio.PUD_DOWN)
        self.pi.stop()
        
    def _log(self, msg):
        if debug:
            print ( self.mCount, msg)
            self.mCount += 1
            
    def measure(self):
        self._log( "measure")
        self.state = 0
        lastState = None
        #
        # expect echo low at start
        #
        echo = self.pi.read(  self.echo)
        self._log( "echo {e:d}".format(e=echo))
        if echo == 1:
            raise HC_SR04_Error(HC_SR04_Error.ECHO_PIN_HIGH)
          
        self.pi.write ( self.trigger, 1)
        time.sleep(0.0001)
        self.pi.write ( self.trigger, 0)
        
        self.cnt = 0
        while self.state != 2:
            if debug: self._log( "state {s:d} cnt {c:d}".format(s=self.state,c=self.cnt))
            if self.state != lastState:
                if debug: self._log( "state {s:d}".format(s=self.state))
                lastState = self.state
                
            self.cnt += 1
            time.sleep(0.002)
            if self.cnt == 25:
                self.pi.write ( self.trigger, 0)
                raise HC_SR04_Error(HC_SR04_Error.NO_RESPONSE)
             
        self._log( "regular exit {s:d}".format(s=self.state))    
        
        return self.t
             
    def _cbf(self, gpio, level, tick):
        if level == 1:
            if debug: self._log( "callback level 1 {t:d} {s:d} cnt {c:d}".format(t= tick, s=self.state, c=self.cnt))
            self.state = 1
            self._high_tick = tick
    
        elif level == 0:
            if debug: self._log( "callback level 0 {t:d} {s:d} cnt {c:d}".format(t= tick, s=self.state, c=self.cnt))
    
            if self._high_tick is not None:
                t = pigpio.tickDiff(self._high_tick, tick)
    
                if debug: self._log( "callback calc time =  {t:d} {s:d} cnt {c:d}".format(t= t, s=self.state, c=self.cnt))
                self.t = t 
            self._log("set state to 2 cnt {c:d}".format( c=self.cnt))      
            self.state = 2
    
    
class HC_SR04_Adapter(adapter.adapters.GPIOAdapter):
    """Build a connection to pigpiod"""
    
    mandatoryParameters = {'poll.interval'}
    
    
    def __init__(self):
        adapter.adapters.GPIOAdapter.__init__(self)
    
    def setActive (self, state):        
        adapter.adapters.GPIOAdapter.setActive(self, state)
            
    def run(self):
        _del = float(self.parameters['poll.interval'])
        if _del < 0.02:
            _del = 0.02
        
        gpio_trigger = self.getChannelByAlias('trigger')    
        gpio_echo = self.getChannelByAlias('echo')    
        
        try:
            hc_sr04 = HC_SR04(gpio_trigger.portNumber, gpio_echo.portNumber)    
        except HC_SR04_Error as e:
            logger.error("{name:s}: Error in connecting to pigpiod {msg:s}".format(name=self.name, msg=e.value))
            self.error(e.value)
            return
        
        last_time = None
        last_error = None
        while not self.stopped():
            #
            self.delay(_del)
            # 
            try:               
                mTime = hc_sr04.measure()
                error = ''
            except HC_SR04_Error as e:
                logger.error("{name:s}: Error in response from HC-SR04 {msg:s}".format(name=self.name, msg=e.value))
                error = e.value
                mTime = 0
            
            if mTime > 20000:
                error ="time too long > 20ms"
                mTime = 0
                
            if last_error != error:
                self.error(error)
                last_error = error
            
            if last_time != mTime:
                self.time( mTime )
                last_time = mTime 

        hc_sr04.stop()
              
    def time(self, value):
        """receives measured time in microseconds, sends seconds towards scratch"""
        if debug:
            print("time", value)
        self.sendValue( float(value)/1000000.0 )    
 
    def error(self, value):
        """error"""
        if debug:
            print("error", value)
        self.sendValue( '"'+ value + '"' )    
 
        
class Pigpiod_PWM_Adapter(adapter.adapters.GPIOAdapter):
    """use pigpiod for PWM"""
    
    mandatoryParameters = {'frequency' : 50, 'rate' : 0.0}
    
    
    def __init__(self):
        adapter.adapters.GPIOAdapter.__init__(self)
        self.pwmrate = 0
        
    def setActive (self, state):        
        adapter.adapters.GPIOAdapter.setActive(self, state)
    
    def _initPWM(self):
        self.pi.set_mode(self.gpios[0].portNumber, pigpio.OUTPUT)
        self.pi.set_pull_up_down(self.gpios[0].portNumber, pigpio.PUD_OFF)
           
        # print(self.gpios[0].portNumber, type(self.gpios[0].portNumber))
        frequency = int( self.parameters['frequency'] )
        self.pi.set_PWM_frequency(self.gpios[0].portNumber, frequency )
                                   
    def run(self):
        if debug: print("thread running")
        
        status = 0
        last_pwmrate =  None
        
        while not self.stopped():

            if status == 0:
                try:    
                    self.pi = pigpio.pi()
                    self._initPWM()
                    with helper.logging.LoggingContext(logger, level=logging.INFO):
                        logger.info("{name:s}: {status:d} connection to pigpiod running".format(name=self.name, status=status))
                    status = 10
                except Exception as e:
                    logger.error("{name:s}: {status:d} could not connect to pigpiod {e:s}".format(name=self.name, status=status, e=str(e) ))
                    logger.warn ("{name:s}: {status:d} start pigpiod with 'sudo pigpiod'".format(name=self.name, status=status))
                    status = 20
                    
            elif status == 10:
                try:
                    if self.isActive():
                        # print(".")
                        if last_pwmrate != self.pwmrate:
                            self.pi.set_PWM_dutycycle( self.gpios[0].portNumber, self.pwmrate )
                            last_pwmrate = self.pwmrate
                    else:
                        self.pi.set_PWM_dutycycle( self.gpios[0].portNumber, 0 )
                except Exception as e:
                    logger.error("{name:s}: {status:d} could not connect to pigpiod {e:s}".format(name=self.name, status=status, e=str(e) ))
                    status = 20
                    
            elif status == 20:
                self.delay(30)
                if not self.stopped():
                    try:    
                        self.pi = pigpio.pi()
                        self._initPWM() 
                        with helper.logging.LoggingContext(logger, level=logging.INFO):
                            logger.info("{name:s}: {status:d} connection to pigpiod running".format(name=self.name, status=status))
                        status = 10
                    except Exception as e:
                        status = 20
                        
            time.sleep(0.075)
        
        try:
            self.pi.set_PWM_dutycycle( self.gpios[0].portNumber, 0 )
        except:
            pass
        if debug: print("thread stopped")
              
    def rate(self, value):
        """receives pwm value from scratch"""
        if debug:
            print("rate", value)
        if self.active:
            v = 0.0
            try:
                v = float(value)
            except:
                logger.error('{name:s}: invalid value: {value:s}'.format(name=self.name, value=str( value)))
                return
            if v < 0.0:
                v  = 0.0
            if v > 100.0:
                v  = 100.0
            
            self.pwmrate = round( 255.0/100.0 * v)

class Pigpiod_DHT11_Adapter(adapter.adapters.GPIOAdapter):
    """use pigpiod for DHT11"""
    
    mandatoryParameters = {}
    
    def __init__(self):
        adapter.adapters.GPIOAdapter.__init__(self)
        
    def setActive (self, state):        
        adapter.adapters.GPIOAdapter.setActive(self, state)
    
    def _initPWM(self):
        self.pi.set_mode(self.gpios[0].portNumber, pigpio.INPUT)
        self.pi.set_pull_up_down(self.gpios[0].portNumber, pigpio.PUD_OFF)
           
    def callback(self, gpio, level, tick):
        r = dict()
        r['level' ] = level
        r['tick' ] = tick
        
        self.pulseCount.append( r) 
                                  
    def run(self):
        if debug: print("thread running")
        
        status = 0
        while not self.stopped():

            if status == 0:
                try:    
                    self.pi = pigpio.pi()
                    self._initPWM()
                    with helper.logging.LoggingContext(logger, level=logging.INFO):
                        logger.info("{name:s}: {status:d} connection to pigpiod running".format(name=self.name, status=status))
                    status = 10
                except Exception as e:
                    logger.error("{name:s}: {status:d} could not connect to pigpiod {e:s}".format(name=self.name, status=status, e=str(e) ))
                    logger.warn ("{name:s}: {status:d} start pigpiod with 'sudo pigpiod'".format(name=self.name, status=status))
                    status = 20
                    
            elif status == 10:
                try:
                    if self.isActive():
                        # print(".")
                        if debug: print("START", self.gpios[0].portNumber)
                        self.pi.set_mode(self.gpios[0].portNumber, pigpio.OUTPUT)
                        self.pi.write(self.gpios[0].portNumber, 0 )
                        time.sleep(0.01)
                        
                        self.pulseCount = []
                        cb = self.pi.callback( self.gpios[0].portNumber, pigpio.EITHER_EDGE, self.callback)
                        time.sleep(0.01)
                        self.pi.set_mode(self.gpios[0].portNumber, pigpio.INPUT)
                        
                        self.delay(2.98)
                        cb.cancel()
                        if debug:
                            print( len( self.pulseCount) )
                            for i in range( 1, len( self.pulseCount) ):
                                
                                if self.pulseCount[i-1] ['level'] == 0 and self.pulseCount[i] ['level'] == 1:
                                    print( i, "0 time", (self.pulseCount[i] ['tick'] - self.pulseCount[i-1] ['tick'] ))
    
                                if self.pulseCount[i-1] ['level'] == 1 and self.pulseCount[i] ['level'] == 0:
                                    print( i, "1 time", (self.pulseCount[i] ['tick'] - self.pulseCount[i-1] ['tick'] ))
                        
                        try:
                            bits = []
                            cnt = 0
                            for i in range( 4, len( self.pulseCount)-1, 2 ):
                                # print("--", i)
                                if self.pulseCount[i-1] ['level'] == 1 and self.pulseCount[i] ['level'] == 0:
                                    tx = self.pulseCount[i] ['tick'] - self.pulseCount[i-1] ['tick']
                                    if ( 18 < tx < 33 ):
                                        bits.append('0')
                                    elif ( 65 < tx < 78 ):
                                        bits.append('1')
                                    else:
                                        raise Exception("out of range {cnt:d}".format(cnt=i) )
                                cnt += 1
                                if cnt == 40:
                                    break
                        except Exception:
                            logger.error("{name:s}: timeframes out of range".format(name=self.name))
                            continue
                        
                        if debug: 
                            print(     bits[ 0:  8], "  ", bits[ 8: 16]  )
                            print(     bits[16: 24], "  ", bits[24: 32], "  ", bits[32: 40]  )
                            print( len(bits) )
                        
                        rh = 0
                        b = 128
                        for i in range( 0, 8):
                            if bits[i] == '1':
                                rh |= b
                            b = b >> 1
                            
                        rf = 0
                        b = 128
                        for i in range( 8, 16):
                            if bits[i] == '1':
                                rf |= b
                            b = b >> 1

                        th = 0
                        b = 128
                        for i in range( 16, 24):
                            if bits[i] == '1':
                                th |= b
                            b = b >> 1

                        tf = 0
                        b = 128
                        for i in range( 24, 32):
                            if bits[i] == '1':
                                tf |= b
                            b = b >> 1
                            
                        cs = 0
                        b = 128
                        for i in range( 32, 40):
                            if bits[i] == '1':
                                cs += b
                            b = b >> 1
                        
                        rh = int(rh)
                        rl = int(rf)
                        th = int(th)
                        tl = int(tf)   
                        
                        if cs != (rh + rl + th + tl) & 0xff:
                            logger.error("{name:s}: checksum mismatch".format(name=self.name))
                            continue
                        humidity    = ((rh <<8) + rf)*0.1
                        temperature = ((th <<8) + tf)*0.1
                        
                        self.humidity    ( str( round( humidity   , 1 )))
                        self.temperature ( str( round( temperature, 1 )))
                        
                        if debug: print( (((rh <<8) +  rf)*0.1), "   ", (((th<<8) + tf)*0.1) )
                                                            
                except Exception as e:
                    logger.error("{name:s}: {status:d} could not connect to pigpiod {e:s}".format(name=self.name, status=status, e=str(e) ))
                    status = 20
                    
            elif status == 20:
                self.delay(30)
                if not self.stopped():
                    try:    
                        self.pi = pigpio.pi()
                        self._initPWM() 
                        with helper.logging.LoggingContext(logger, level=logging.INFO):
                            logger.info("{name:s}: {status:d} connection to pigpiod running".format(name=self.name, status=status))
                        status = 10
                    except Exception as e:
                        status = 20
                        
        if debug: print("thread stopped")
              
    def humidity(self, value):
        """output from adapter to scratch."""
        self.sendValue(value)
        
    def temperature(self, value):
        """output from adapter to scratch."""
        self.sendValue(value)
        