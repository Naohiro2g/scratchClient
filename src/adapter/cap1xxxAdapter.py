# -*- coding: utf-8 -*-
    # --------------------------------------------------------------------------------------------
    # Copyright (C) 2017  Gerhard Hepp
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
    #
    # Part of this code is based on work from pimoroni 
    # published in https://github.com/pimoroni/cap1xxx/blob/master/library/cap1xxx.py
    # ---------------------------------------------------------------------------------------------
    

import math
import time
import adapter
import threading
from i2c.manager import I2CManager
import sys

import logging
logger = logging.getLogger(__name__)

debug = False

# --------------------------------------------------------------------------------------
class CAP1208Adapter (adapter.adapters.I2CAdapter):
    """CAP1208"""
    

    mandatoryParameters = { 'poll.interval': '0.2', 
                           'i2c.bus' : '1', 
                           'i2c.address' :'0x28' }
    

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self )

    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up I2C
        #
        adapter.adapters.I2CAdapter.setActive(self, state);

    def run(self):
        if debug:
            print(self.name, "run()")
        _del = float(self.parameters['poll.interval'])

        ret = self._init() 
        if not ret:
            return
            
             
        while not self.stopped():
            #
            # delay 5 sec, but break time in small junks to allow stopping fast
            #
            self.delay(_del)
            _is = self._interrupt_status()
            if not _is:
                continue
            inputs = self.get_input_status()
            self.clear_interrupt()
            
            print("{s0:10s} {s1:10s} {s2:10s} {s3:10s} {s4:10s} {s5:10s} {s6:10s} {s7:10s}".format( s0=inputs[0],
                                                                                                    s1=inputs[1],
                                                                                                    s2=inputs[2],
                                                                                                    s3=inputs[3],
                                                                                                    s4=inputs[4],
                                                                                                    s5=inputs[5],
                                                                                                    s6=inputs[6],
                                                                                                    s7=inputs[7]  ) )  

            if inputs[0] == 'press': self.s0_pressed()
            if inputs[1] == 'press': self.s1_pressed()
            if inputs[2] == 'press': self.s2_pressed()
            if inputs[3] == 'press': self.s3_pressed()
            if inputs[4] == 'press': self.s4_pressed()
            if inputs[5] == 'press': self.s5_pressed()
            if inputs[6] == 'press': self.s6_pressed()
            if inputs[7] == 'press': self.s7_pressed()
            
            if inputs[0] == 'release': self.s0_released()
            if inputs[1] == 'release': self.s1_released()
            if inputs[2] == 'release': self.s2_released()
            if inputs[3] == 'release': self.s3_released()
            if inputs[4] == 'release': self.s4_released()
            if inputs[5] == 'release': self.s5_released()
            if inputs[6] == 'release': self.s6_released()
            if inputs[7] == 'release': self.s7_released()

    def s0_pressed(self):
        """output from adapter to scratch."""
        self.send()
    def s1_pressed(self):
        """output from adapter to scratch."""
        self.send()
    def s2_pressed(self):
        """output from adapter to scratch."""
        self.send()
    def s3_pressed(self):
        """output from adapter to scratch."""
        self.send()
    def s4_pressed(self):
        """output from adapter to scratch."""
        self.send()
    def s5_pressed(self):
        """output from adapter to scratch."""
        self.send()
    def s6_pressed(self):
        """output from adapter to scratch."""
        self.send()
    def s7_pressed(self):
        """output from adapter to scratch."""
        self.send()

    def s0_released(self):
        """output from adapter to scratch."""
        self.send()
    def s1_released(self):
        """output from adapter to scratch."""
        self.send()
    def s2_released(self):
        """output from adapter to scratch."""
        self.send()
    def s3_released(self):
        """output from adapter to scratch."""
        self.send()
    def s4_released(self):
        """output from adapter to scratch."""
        self.send()
    def s5_released(self):
        """output from adapter to scratch."""
        self.send()
    def s6_released(self):
        """output from adapter to scratch."""
        self.send()
    def s7_released(self):
        """output from adapter to scratch."""
        self.send()
    
    # Supported devices
    PID_CAP1208 = 0b01101011
    PID_CAP1188 = 0b01010000
    PID_CAP1166 = 0b01010001

    #
    # The register definitions and part of the code 
    # are taken from the adafruit libraries
    # REGISTER MAP
    
    R_MAIN_CONTROL                  = 0x00
    R_GENERAL_STATUS                = 0x02
    R_SENSOR_INPUT_STATUS           = 0x03
    
    R_NOISE_FLAG_STATUS             = 0x0A
    
    # Read-only delta counts for all inputs
    R_SENSOR_INPUT_1_DELTA_COUNT   = 0x10
    R_SENSOR_INPUT_2_DELTA_COUNT   = 0x11
    R_SENSOR_INPUT_3_DELTA_COUNT   = 0x12
    R_SENSOR_INPUT_4_DELTA_COUNT   = 0x13
    R_SENSOR_INPUT_5_DELTA_COUNT   = 0x14
    R_SENSOR_INPUT_6_DELTA_COUNT   = 0x15
    R_SENSOR_INPUT_7_DELTA_COUNT   = 0x16
    R_SENSOR_INPUT_8_DELTA_COUNT   = 0x17
    
    R_SENSITIVITY_CONTROL           = 0x1F
    # B7     = N/A
    # B6..B4 = Sensitivity
    # B3..B0 = Base Shift
    SENSITIVITY = {128: 0b000, 64:0b001, 32:0b010, 16:0b011, 8:0b100, 4:0b100, 2:0b110, 1:0b111}
    
    R_CONFIGURATION                 = 0x20
    # B7 = Timeout
    # B6 = Wake Config ( 1 = Wake pin asserted )
    # B5 = Disable Digital Noise ( 1 = Noise threshold disabled )
    # B4 = Disable Analog Noise ( 1 = Low frequency analog noise blocking disabled )
    # B3 = Max Duration Recalibration ( 1 =  Enable recalibration if touch is held longer than max duration )
    # B2..B0 = N/A

    R_SENSOR_INPUT_ENABLE    = 0x21


    R_INPUT_CONFIG    = 0x22

    R_INPUT_CONFIG2   = 0x23 # Default 0x00000111

    # Values for bits 3 to 0 of R_INPUT_CONFIG2
    # Determines minimum amount of time before
    # a "press and hold" event is detected.
    
    # Also - Values for bits 3 to 0 of R_INPUT_CONFIG
    # Determines rate at which interrupt will repeat
    #
    # Resolution of 35ms, max = 35 + (35 * 0b1111) = 560ms
    
    R_SAMPLING_CONFIG = 0x24 # Default 0x00111001
    R_CALIBRATION     = 0x26 # Default 0b00000000
    R_INTERRUPT_EN    = 0x27 # Default 0b11111111
    R_REPEAT_EN       = 0x28 # Default 0b11111111
    R_MTOUCH_CONFIG   = 0x2A # Default 0b11111111
    R_MTOUCH_PAT_CONF = 0x2B
    R_MTOUCH_PATTERN  = 0x2D
    R_COUNT_O_LIMIT   = 0x2E
    R_RECALIBRATION   = 0x2F
    
    # R/W Touch detection thresholds for inputs
    R_INPUT_1_THRESH  = 0x30
    R_INPUT_2_THRESH  = 0x31
    R_INPUT_3_THRESH  = 0x32
    R_INPUT_4_THRESH  = 0x33
    R_INPUT_4_THRESH  = 0x34
    R_INPUT_6_THRESH  = 0x35
    R_INPUT_7_THRESH  = 0x36
    R_INPUT_8_THRESH  = 0x37
    
    # R/W Noise threshold for all inputs
    R_NOISE_THRESH    = 0x38
    
    # R/W Standby and Config Registers
    R_STANDBY_CHANNEL = 0x40
    R_STANDBY_CONFIG  = 0x41
    R_STANDBY_SENS    = 0x42
    R_STANDBY_THRESH  = 0x43
    
    R_CONFIGURATION2  = 0x44
    # B7 = Linked LED Transition Controls ( 1 = LED trigger is !touch )
    # B6 = Alert Polarity ( 1 = Active Low Open Drain, 0 = Active High Push Pull )
    # B5 = Reduce Power ( 1 = Do not power down between poll )
    # B4 = Link Polarity/Mirror bits ( 0 = Linked, 1 = Unlinked )
    # B3 = Show RF Noise ( 1 = Noise status registers only show RF, 0 = Both RF and EMI shown )
    # B2 = Disable RF Noise ( 1 = Disable RF noise filter )
    # B1..B0 = N/A
    
    # Read-only reference counts for sensor inputs
    R_INPUT_1_BCOUNT  = 0x50
    R_INPUT_2_BCOUNT  = 0x51
    R_INPUT_3_BCOUNT  = 0x52
    R_INPUT_4_BCOUNT  = 0x53
    R_INPUT_5_BCOUNT  = 0x54
    R_INPUT_6_BCOUNT  = 0x55
    R_INPUT_7_BCOUNT  = 0x56
    R_INPUT_8_BCOUNT  = 0x57
    
    # LED Controls - For CAP1188 and similar
    R_LED_OUTPUT_TYPE = 0x71
    R_LED_LINKING     = 0x72
    R_LED_POLARITY    = 0x73
    R_LED_OUTPUT_CON  = 0x74
    R_LED_LTRANS_CON  = 0x77
    R_LED_MIRROR_CON  = 0x79
    
    # LED Behaviour
    R_LED_BEHAVIOUR_1 = 0x81 # For LEDs 1-4
    R_LED_BEHAVIOUR_2 = 0x82 # For LEDs 5-8
    R_LED_PULSE_1_PER = 0x84
    R_LED_PULSE_2_PER = 0x85
    R_LED_BREATHE_PER = 0x86
    R_LED_CONFIG      = 0x88
    R_LED_PULSE_1_DUT = 0x90
    R_LED_PULSE_2_DUT = 0x91
    R_LED_BREATHE_DUT = 0x92
    R_LED_DIRECT_DUT  = 0x93
    R_LED_DIRECT_RAMP = 0x94
    R_LED_OFF_DELAY   = 0x95
    
    # R/W Power buttonc ontrol
    R_POWER_BUTTON    = 0x60
    R_POW_BUTTON_CONF = 0x61
    
    # Read-only upper 8-bit calibration values for sensors
    R_INPUT_1_CALIB   = 0xB1
    R_INPUT_2_CALIB   = 0xB2
    R_INPUT_3_CALIB   = 0xB3
    R_INPUT_4_CALIB   = 0xB4
    R_INPUT_5_CALIB   = 0xB5
    R_INPUT_6_CALIB   = 0xB6
    R_INPUT_7_CALIB   = 0xB7
    R_INPUT_8_CALIB   = 0xB8
    
    # Read-only 2 LSBs for each sensor input
    R_INPUT_CAL_LSB1  = 0xB9
    R_INPUT_CAL_LSB2  = 0xBA
    
    # Product ID Registers
    R_PRODUCT_ID      = 0xFD
    R_MANUFACTURER_ID = 0xFE
    R_REVISION        = 0xFF
    

    def _init(self):
        
        self.number_of_inputs = 8
        
        self.last_input_status = [False]  * self.number_of_inputs
        self.input_status      = ['none'] * self.number_of_inputs
        self.input_delta       = [0] * self.number_of_inputs
        self.input_pressed     = [False]  * self.number_of_inputs
        self.repeat_enabled    = 0b00000000
        self.release_enabled   = 0b11111111
        
        productId = self._get_product_id()
        if productId != self.PID_CAP1208:
            logger.error("{n:s}: Chip product id not matching CAP1208".format(n=self.name))
            return False
        return True

        # Enable all inputs with interrupt by default
        self.enable_inputs(0b11111111)
        self.enable_interrupts(0b11111111)

        # Disable repeat for all channels, but give
        # it sane defaults anyway
        self.enable_repeat(0b00000000)
        self.enable_multitouch(True)

        self.set_hold_delay(210)
        self.set_repeat_rate(210)

        # Tested sane defaults for various configurations
        self.write8(self.R_SAMPLING_CONFIG, 0b00001000) # 1sample per measure, 1.28ms time, 35ms cycle
        self.write8(self.R_SENSITIVITY,     0b01100000) # 2x sensitivity
        self.write8(self.R_GENERAL_CONFIG,  0b00111000)
        self.write8(self.R_CONFIGURATION2,  0b01100000)
        self.set_touch_delta(10)
    
    def filter_analog_noise(self, value):
        self._change_bit(self.R_GENERAL_CONFIG, 4, not value)
        
    def filter_digital_noise(self, value):
        self._change_bit(self.R_GENERAL_CONFIG, 5, not value)

    def set_hold_delay(self, ms):
        """Set time before a press and hold is detected,
        Clamps to multiples of 35 from 35 to 560"""
        repeat_rate = self._calc_touch_rate(ms)
        input_config = self.readU8(self.R_INPUT_CONFIG2)
        input_config = (input_config & ~0b1111) | repeat_rate
        self.write8(self.R_INPUT_CONFIG2, input_config)

    def set_repeat_rate(self, ms):
        """Set repeat rate in milliseconds, 
        Clamps to multiples of 35 from 35 to 560"""
        repeat_rate = self._calc_touch_rate(ms)
        input_config = self.readU8(self.R_INPUT_CONFIG)
        input_config = (input_config & ~0b1111) | repeat_rate
        self.write8(self.R_INPUT_CONFIG, input_config)

    def _calc_touch_rate(self, ms):
        ms = min(max(ms,0),560)
        scale = int((round(ms / 35.0) * 35) - 35) / 35
        return int(scale)

    def _get_product_id(self):
        return self.readU8(self.R_PRODUCT_ID)
   
    def enable_multitouch(self, en=True):
        """Toggles multi-touch by toggling the multi-touch
        block bit in the config register"""
        ret_mt = self.readU8(self.R_MTOUCH_CONFIG)
        if en:
            self.write8(self.R_MTOUCH_CONFIG, ret_mt & ~0x80)
        else:
            self.write8(self.R_MTOUCH_CONFIG, ret_mt | 0x80 )

    def _interrupt_status(self):
        return self.readU8(self.R_MAIN_CONTROL) & 1
    
    def clear_interrupt(self):
        """Clear the interrupt flag, bit 0, of the
        main control register"""
        main = self.readU8(self.R_MAIN_CONTROL)
        main &= ~0b00000001
        self.write8(self.R_MAIN_CONTROL, main)

    def enable_repeat(self, inputs):
        self.repeat_enabled = inputs
        self.write8(self.R_REPEAT_EN, inputs)

    def enable_interrupts(self, inputs):
        self.write8(self.R_INTERRUPT_EN, inputs)

    def enable_inputs(self, inputs):
        self.write8(self.R_INPUT_ENABLE, inputs)

                    
    def get_input_status(self):
        """Get the status of all inputs.
        Returns an array of 8 boolean values indicating
        whether an input has been triggered since the
        interrupt flag was last cleared."""
        
        touched = self.readU8(self.R_SENSOR_INPUT_STATUS)
        threshold = self.readList( self.R_INPUT_1_THRESH, self.number_of_inputs)
        delta = self.readList(self.R_SENSOR_INPUT_1_DELTA_COUNT, self.number_of_inputs)
        #status = ['none'] * 8
        
        for x in range(self.number_of_inputs):
            if (1 << x) & touched:
                status = 'none'
                _delta = self._get_twos_comp(delta[x]) 
                #threshold = self._read_byte(R_INPUT_1_THRESH + x)
                # We only ever want to detect PRESS events
                # If repeat is disabled, and release detect is enabled
                if _delta >= threshold[x]: # self._delta:
                    self.input_delta[x] = _delta
                    #  Touch down event
                    if self.input_status[x] in ['press','held']:
                        if self.repeat_enabled & (1 << x):
                            status = 'held'
                    if self.input_status[x] in ['none','release']:
                        if self.input_pressed[x]:
                            status = 'none'
                        else:
                            status = 'press'
                else:
                    # Touch release event
                    if self.release_enabled & (1 << x) and not self.input_status[x] == 'release':
                        status = 'release'
                    else:
                        status = 'none'

                self.input_status[x] = status
                self.input_pressed[x] = status in ['press','held','none']
            else:
                self.input_status[x] = 'none'
                self.input_pressed[x] = False
        return self.input_status
    
    def _get_twos_comp(self,val):
        if ( val & (1<< (8 - 1))) != 0:
            val = val - (1 << 8)
        return val
