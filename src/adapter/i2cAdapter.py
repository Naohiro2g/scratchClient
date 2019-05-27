# -*- coding: utf-8 -*-
    # --------------------------------------------------------------------------------------------
    # Copyright (C) 2013  Gerhard Hepp
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

import math
import time
import adapter
import threading
from i2c.manager import I2CManager

import logging
logger = logging.getLogger(__name__)

debug = False

# --------------------------------------------------------------------------------------
class ADC_ADS1015_Input (adapter.adapters.I2CAdapter):
    """ADC Interface for ADS1015"""


    mandatoryParameters = { 'poll.interval': '0.2',
                           'i2c.bus' : '1',
                           'i2c.address' :'0',
                           'adc.channel' : '0' }

    optionalParameters = { 'adc.pga': '4096',
                           'adc.sps' : '250' }

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self )
        self.lockPWMAccess = threading.Lock()

    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up SPI
        #
        adapter.adapters.I2CAdapter.setActive(self, state);

    def run(self):
        if debug:
            print(self.name, "run()")
        _del = float(self.parameters['poll.interval'])

        self.int_adc_channel=   int(self.parameters['adc.channel'])

        self.adc_pga =   int( self.parameters.get('adc.pga', 0) )

        if self.adc_pga in ADC_ADS1015_Input.pgaADS1x15:
            pass
        else:
            logger.warn("{n:s}: config parameter 'adc.pga'={v:d} not in allowed range".format(n=self.name, v=self.adc_pga))
            self.adc_pga = 4096

        self.adc_sps =   int( self.parameters.get('adc.sps', 0) )
        if self.adc_sps in ADC_ADS1015_Input.spsADS1015:
            pass
        else:
            logger.warn("{n:s}: config parameter 'adc.sps'={v:d} not in allowed range".format(n=self.name, v=self.adc_sps))
            self.adc_sps = 250

        self.adc_sps =   int( self.parameters['adc.sps'] )
        last = self._getValue(
                                self.int_i2c_address,
                                self.int_adc_channel
                                )
        self.adc(last)

        while not self.stopped():
            #
            # delay 5 sec, but break time in small junks to allow stopping fast
            #
            self.delay(_del)

            current = self._getValue(
                                self.int_i2c_address,
                                self.int_adc_channel
                                )

            # plus/minus zwei Punkte ist noch 'identisch'

            if not( last -2 < current < last + 2) :
                self.adc( current )
                last = current

    def adc(self, value):
        """output from adapter to scratch."""
        self.sendValue(str(value))

    #
    # The register definitions and part of the code
    # are taken from the adafruit libraries
    #
    # Pointer Register
    __ADS1015_REG_POINTER_MASK        = 0x03
    __ADS1015_REG_POINTER_CONVERT     = 0x00
    __ADS1015_REG_POINTER_CONFIG      = 0x01
    __ADS1015_REG_POINTER_LOWTHRESH   = 0x02
    __ADS1015_REG_POINTER_HITHRESH    = 0x03

    # Config Register
    __ADS1015_REG_CONFIG_OS_MASK      = 0x8000
    __ADS1015_REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
    __ADS1015_REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit = 0 when conversion is in progress
    __ADS1015_REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit = 1 when device is not performing a conversion

    __ADS1015_REG_CONFIG_MUX_MASK     = 0x7000
    __ADS1015_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 (default)
    __ADS1015_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    __ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    __ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    __ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    __ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

    __ADS1015_REG_CONFIG_PGA_MASK     = 0x0E00
    __ADS1015_REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range
    __ADS1015_REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range
    __ADS1015_REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range (default)
    __ADS1015_REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range
    __ADS1015_REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range
    __ADS1015_REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range

    __ADS1015_REG_CONFIG_MODE_MASK    = 0x0100
    __ADS1015_REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
    __ADS1015_REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default)

    __ADS1015_REG_CONFIG_DR_MASK      = 0x00E0
    __ADS1015_REG_CONFIG_DR_128SPS    = 0x0000  # 128 samples per second
    __ADS1015_REG_CONFIG_DR_250SPS    = 0x0020  # 250 samples per second
    __ADS1015_REG_CONFIG_DR_490SPS    = 0x0040  # 490 samples per second
    __ADS1015_REG_CONFIG_DR_920SPS    = 0x0060  # 920 samples per second
    __ADS1015_REG_CONFIG_DR_1600SPS   = 0x0080  # 1600 samples per second (default)
    __ADS1015_REG_CONFIG_DR_2400SPS   = 0x00A0  # 2400 samples per second
    __ADS1015_REG_CONFIG_DR_3300SPS   = 0x00C0  # 3300 samples per second (also 0x00E0)

    __ADS1015_REG_CONFIG_CQUE_MASK    = 0x0003
    __ADS1015_REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
    __ADS1015_REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
    __ADS1015_REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
    __ADS1015_REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

    __ADS1015_REG_CONFIG_CMODE_MASK   = 0x0010
    __ADS1015_REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis (default)
    __ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

    __ADS1015_REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
    __ADS1015_REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator (default)
    __ADS1015_REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

    __ADS1015_REG_CONFIG_CPOL_MASK    = 0x0008
    __ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active (default)
    __ADS1015_REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

    spsADS1015 = {
                    128:__ADS1015_REG_CONFIG_DR_128SPS,
                    250:__ADS1015_REG_CONFIG_DR_250SPS,
                    490:__ADS1015_REG_CONFIG_DR_490SPS,
                    920:__ADS1015_REG_CONFIG_DR_920SPS,
                    1600:__ADS1015_REG_CONFIG_DR_1600SPS,
                    2400:__ADS1015_REG_CONFIG_DR_2400SPS,
                    3300:__ADS1015_REG_CONFIG_DR_3300SPS
                  }
    # Dictionariy with the programable gains
    pgaADS1x15 = {
                    6144:__ADS1015_REG_CONFIG_PGA_6_144V,
                    4096:__ADS1015_REG_CONFIG_PGA_4_096V,
                    2048:__ADS1015_REG_CONFIG_PGA_2_048V,
                    1024:__ADS1015_REG_CONFIG_PGA_1_024V,
                    512: __ADS1015_REG_CONFIG_PGA_0_512V,
                    256: __ADS1015_REG_CONFIG_PGA_0_256V
                  }

    def _getValue(self, i2caddress, channel):
        #
        # multithreading, there could be simultaneous access to one devive.
        # therefore: lock the procedure.
        #
        try:
            self.i2cManager.getLock( self.int_i2c_bus, self.int_i2c_address ).acquire()
            #
            # Samples per Second
            #
            sps=490
            #
            # Programmablae Gain adjust
            #
            pga = 4096
            #
            # Disable comparator, Non-latching, Alert/Rdy active low
            # traditional comparator, single-shot mode
            config = self.__ADS1015_REG_CONFIG_CQUE_NONE    | \
                     self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
                     self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
                     self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
                     self.__ADS1015_REG_CONFIG_MODE_SINGLE

            # Set sample per seconds, defaults to 250sps
            # If sps is in the dictionary (defined in init) it returns the value of the constant
            # othewise it returns the value for 250sps. This saves a lot of if/elif/else code!
            config |= self.spsADS1015.setdefault(sps, self.__ADS1015_REG_CONFIG_DR_1600SPS)

            # Set PGA/voltage range, defaults to +-6.144V
            if ( (pga not in self.pgaADS1x15) ):
                logger.error( "ADS1x15: Invalid pga specified: {pga:d}, using 6144mV".format(pga=pga))

            config |= self.pgaADS1x15.setdefault(pga, self.__ADS1015_REG_CONFIG_PGA_4_096V)
            self.pga = pga

            # Set the channel to be converted
            if channel == 3:
                config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_3
            elif channel == 2:
                config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_2
            elif channel == 1:
                config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_1
            else:
                config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_0

            # Set 'start single-conversion' bit
            config |= self.__ADS1015_REG_CONFIG_OS_SINGLE

            # Write config register to the ADC
            _bytes = [(config >> 8) & 0xFF, config & 0xFF]

            self.writeList( self.__ADS1015_REG_POINTER_CONFIG, _bytes)

            # Wait for the ADC conversion to complete
            # The minimum delay depends on the sps: delay >= 1/sps
            # We add 0.1ms to be sure
            delay = 1.0/ float(sps) +0.0001
            time.sleep(delay)

            # Read the conversion results

            result = self.readList( self.__ADS1015_REG_POINTER_CONVERT, 2)
        finally:
            self.i2cManager.getLock(self.int_i2c_bus, self.int_i2c_address ).release()

        if debug:
            print("{n:s}: {r0:02x} {r1:02x} ".format( n=self.name, r0 = result[0], r1=result[1]))
        # Shift right 4 bits for the 12-bit ADS1015 and convert to mV
        return ( (result[0] << 4) | (result[1]  >> 4 ) ) *pga/2048.0


# --------------------------------------------------------------------------------------
class Luminosity_BH1750_Input (adapter.adapters.I2CAdapter):
    """Luminosity Sensor BH1750"""


    mandatoryParameters = { 'poll.interval': '0.5',
                           'i2c.bus' : '1',
                           'i2c.address' :'0x5c'
                          }

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self)


    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up SPI
        #
        adapter.adapters.I2CAdapter.setActive(self, state)

    def run(self):
        if debug:
            print(self.name, "run()")
        _del = float(self.parameters['poll.interval'])

        last = self.getValue(
                               self.int_i2c_address
                            )
        if last != None:
            self.luminosity(last)

        while not self.stopped():
            #
            # delay 5 sec, but break time in small junks to allow stopping fast
            #
            self.delay(_del)

            current = self.getValue(
                                self.int_i2c_address
                                )
            if current != None:
                # plus/minus zwei Punkte ist noch 'identisch'

                if not( last -1 < current < last + 1) :
                    self.luminosity( current )
                    last = current

    def luminosity(self, value):
        """output from adapter to scratch."""
        self.sendValue(str(value))

    __BH1750_READ_LUMINOSITY_1LX = 0b00100000
    __BH1750_READ_LUMINOSITY_4LX = 0b00100011


    def getValue(self, i2cdata):
        #
        # data = self.readList (self.__BH1750_READ_LUMINOSITY_1LX, 2 )
        data = self.bus.read_i2c_block_data(self.int_i2c_address, self.__BH1750_READ_LUMINOSITY_1LX)
        if data == None:
            return None

        i = data[1] + 256 * data[0]

        if (debug):
            print("{dh:08b} {dl:08b} {lx:016b}".format(dh=data[0], dl=data[1], lx=i))
            print ("Luminosity 4 lx {lx:6.2f} lx".format( lx = ( float(i)/1.2)))

        return float(i) / 1.2

# --------------------------------------------------------------------------------------

class Pressure_BMP085_Input (adapter.adapters.I2CAdapter):
    """Pressure Sensor BMP085
       based on code from adafruit.com
    """


    mandatoryParameters = { 'poll.interval': '1.0',
                           'i2c.bus' : '1',
                           'i2c.address' :'0x5c'
                          }

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self)


    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up SPI
        #
        adapter.adapters.I2CAdapter.setActive(self, state)

    def run(self):
        if debug:
            print(self.name, "run()")
        _del = float(self.parameters['poll.interval'])

        last = self.getValues()
        # TODO: create new send api for dictionaries
        self.pressure(last['pressure'])
        self.temperature(last['temperature'])

        while not self.stopped():
            #
            # delay 5 sec, but break time in small junks to allow stopping fast
            #
            self.delay(_del)

            current = self.getValues()
            if current['pressure'] != last['pressure']:
                self.pressure( current['pressure'] )
                last['pressure'] = current['pressure']

            if current['temperature'] != last['temperature']:
                self.temperature( current['temperature'] )
                last['temperature'] = current['temperature']

    # Operating Modes
    BMP085_ULTRALOWPOWER     = 0
    BMP085_STANDARD          = 1
    BMP085_HIGHRES           = 2
    BMP085_ULTRAHIGHRES      = 3

    # BMP085 Registers
    BMP085_CAL_AC1           = 0xAA  # R   Calibration data (16 bits)
    BMP085_CAL_AC2           = 0xAC  # R   Calibration data (16 bits)
    BMP085_CAL_AC3           = 0xAE  # R   Calibration data (16 bits)
    BMP085_CAL_AC4           = 0xB0  # R   Calibration data (16 bits)
    BMP085_CAL_AC5           = 0xB2  # R   Calibration data (16 bits)
    BMP085_CAL_AC6           = 0xB4  # R   Calibration data (16 bits)
    BMP085_CAL_B1            = 0xB6  # R   Calibration data (16 bits)
    BMP085_CAL_B2            = 0xB8  # R   Calibration data (16 bits)
    BMP085_CAL_MB            = 0xBA  # R   Calibration data (16 bits)
    BMP085_CAL_MC            = 0xBC  # R   Calibration data (16 bits)
    BMP085_CAL_MD            = 0xBE  # R   Calibration data (16 bits)
    BMP085_CONTROL           = 0xF4
    BMP085_TEMPDATA          = 0xF6
    BMP085_PRESSUREDATA      = 0xF6

    # Commands
    BMP085_READTEMPCMD       = 0x2E
    BMP085_READPRESSURECMD   = 0x34

    def _load_calibration(self):
        #
        # readS16BE replaced by readS16
        # readU16BE replaced by readU16
        #
        self.cal_AC1 = self.readS16(self.BMP085_CAL_AC1)   # INT16
        self.cal_AC2 = self.readS16(self.BMP085_CAL_AC2)   # INT16
        self.cal_AC3 = self.readS16(self.BMP085_CAL_AC3)   # INT16

        self.cal_AC4 = self.readU16(self.BMP085_CAL_AC4)   # UINT16
        self.cal_AC5 = self.readU16(self.BMP085_CAL_AC5)   # UINT16
        self.cal_AC6 = self.readU16(self.BMP085_CAL_AC6)   # UINT16

        self.cal_B1 = self.readS16(self.BMP085_CAL_B1)     # INT16
        self.cal_B2 = self.readS16(self.BMP085_CAL_B2)     # INT16
        self.cal_MB = self.readS16(self.BMP085_CAL_MB)     # INT16
        self.cal_MC = self.readS16(self.BMP085_CAL_MC)     # INT16
        self.cal_MD = self.readS16(self.BMP085_CAL_MD)     # INT16

    def _display_calibration(self):

        print ('_display_calibration', logger)

        logger.info('AC1 = {0:6d}'.format(self.cal_AC1))
        logger.info('AC2 = {0:6d}'.format(self.cal_AC2))
        logger.info('AC3 = {0:6d}'.format(self.cal_AC3))
        logger.info('AC4 = {0:6d}'.format(self.cal_AC4))
        logger.info('AC5 = {0:6d}'.format(self.cal_AC5))
        logger.info('AC6 = {0:6d}'.format(self.cal_AC6))
        logger.info('B1 = {0:6d}'.format(self.cal_B1))
        logger.info('B2 = {0:6d}'.format(self.cal_B2))
        logger.info('MB = {0:6d}'.format(self.cal_MB))
        logger.info('MC = {0:6d}'.format(self.cal_MC))
        logger.info('MD = {0:6d}'.format(self.cal_MD))

    def _load_datasheet_calibration(self):
        # Set calibration from values in the datasheet example.  Useful for debugging the
        # temp and pressure calculation accuracy.
        self.cal_AC1 = 408
        self.cal_AC2 = -72
        self.cal_AC3 = -14383
        self.cal_AC4 = 32741
        self.cal_AC5 = 32757
        self.cal_AC6 = 23153
        self.cal_B1 = 6190
        self.cal_B2 = 4
        self.cal_MB = -32767
        self.cal_MC = -8711
        self.cal_MD = 2868

    def read_raw_temp(self):
        """Reads the raw (uncompensated) temperature from the sensor."""
        self.write8(self.BMP085_CONTROL, self.BMP085_READTEMPCMD)
        time.sleep(0.005)  # Wait 5ms

        raw = self.readU16(self.BMP085_TEMPDATA)
        logger.debug('Raw temp 0x{0:X} ({1})'.format(raw & 0xFFFF, raw))
        return raw

    def read_raw_pressure(self):
        """Reads the raw (uncompensated) pressure level from the sensor."""
        self.write8(self.BMP085_CONTROL, self.BMP085_READPRESSURECMD + (self._mode << 6))
        if self._mode == self.BMP085_ULTRALOWPOWER:
            time.sleep(0.005)
        elif self._mode == self.BMP085_HIGHRES:
            time.sleep(0.014)
        elif self._mode == self.BMP085_ULTRAHIGHRES:
            time.sleep(0.026)
        else:
            time.sleep(0.008)
        msb = self.readU8(self.BMP085_PRESSUREDATA)
        lsb = self.readU8(self.BMP085_PRESSUREDATA+1)
        xlsb = self.readU8(self.BMP085_PRESSUREDATA+2)
        raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self._mode)
        logger.debug('Raw pressure 0x{0:04X} ({1})'.format(raw & 0xFFFF, raw))
        return raw

    def read_temperature(self):
        """Gets the compensated temperature in degrees celsius."""
        UT = self.read_raw_temp()
        # Datasheet value for debugging:
        #UT = 27898
        # Calculations below are taken straight from section 3.5 of the datasheet.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) / (X1 + self.cal_MD)
        B5 = X1 + X2

        logger.debug("X1 = {x:d}".format(x=X1))
        logger.debug("X2 = {x:d}".format(x=X2))
        logger.debug("B5 = {x:d}".format(x=B5))

        temp = ((B5 + 8) >> 4) / 10.0
        logger.debug('Calibrated temperature {0} C'.format(temp))
        return temp

    def read_pressure(self):
        """Gets the compensated pressure in Pascals."""
        UT = self.read_raw_temp()
        UP = self.read_raw_pressure()
        # Datasheet values for debugging:
        #UT = 27898
        #UP = 23843
        # Calculations below are taken straight from section 3.5 of the datasheet.
        # Calculate true temperature coefficient B5.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) / (X1 + self.cal_MD)
        B5 = X1 + X2
        logger.debug('B5 = {0}'.format(B5))
        # Pressure Calculations
        B6 = B5 - 4000
        logger.debug('B6 = {0}'.format(B6))
        X1 = (self.cal_B2 * (B6 * B6) >> 12) >> 11
        X2 = (self.cal_AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.cal_AC1 * 4 + X3) << self._mode) + 2) / 4
        logger.debug('B3 = {0}'.format(B3))
        X1 = (self.cal_AC3 * B6) >> 13
        X2 = (self.cal_B1 * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.cal_AC4 * (X3 + 32768)) >> 15
        logger.debug('B4 = {0}'.format(B4))
        B7 = (UP - B3) * (50000 >> self._mode)
        logger.debug('B7 = {0}'.format(B7))
        if B7 < 0x80000000:
            p = (B7 * 2) / B4
        else:
            p = (B7 / B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        logger.debug('Pressure {0} Pa'.format(p))
        return p

    def read_altitude(self, sealevel_pa=101325.0):
        """Calculates the altitude in meters."""
        # Calculation taken straight from section 3.6 of the datasheet.
        pressure = float(self.read_pressure())
        altitude = 44330.0 * (1.0 - pow(pressure / sealevel_pa, (1.0/5.255)))
        logger.debug('Altitude {0} m'.format(altitude))
        return altitude

    def read_sealevel_pressure(self, altitude_m=0.0):
        """Calculates the pressure at sealevel when given a known altitude in
        meters. Returns a value in Pascals."""
        pressure = float(self.read_pressure())
        p0 = pressure / pow(1.0 - altitude_m/44330.0, 5.255)
        logger.debug('Sealevel pressure {0} Pa'.format(p0))
        return p0


    def getValues(self):
        """return dictionary with values"""

        self._mode = self.BMP085_STANDARD

        self._load_calibration()
        if debug:
            self._display_calibration()
        pressure = self.read_pressure()
        temperature=self.read_temperature()

        return { 'temperature': temperature, 'pressure': pressure}



    def pressure(self, value):
        """output from adapter to scratch."""
        self.sendValue(str(value))

    def temperature(self, value):
        """output from adapter to scratch."""
        self.sendValue(str(value))

# --------------------------------------------------------------------------------------
class PWM_PCA9685 (adapter.adapters.I2CAdapter):
    """16-channel, 12-bit PWM Fm+ I2C-bus LED controller
       Based on a script from adafruit."""

    __MODE1              = 0x00
    __MODE2              = 0x01
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04

    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09


    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD
    __PRE_SCALE          = 0xFE

    mandatoryParameters = {
                           'i2c.bus' : '1',
                           'i2c.address' :'0x40',  # cloud be 0x40 - 0x7f (0x43 - 0x77 by i2c)
                           'frequency' : '50'      # Hz
                          }

    frequency = 50
    K_servo_min = 1.0
    K_servo_max = 2.0
    K_servo_scale = 180

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self)


    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up SPI
        #
        adapter.adapters.I2CAdapter.setActive(self, state)
        if state:
            self._reset()
            frequency = float(self.parameters['frequency'])
            self._setFrequency(
                                    self.int_i2c_bus,
                                    self.int_i2c_address,
                                    frequency
                                    )

    def run(self):
        pass

    def _setFrequency (self, bus, address, frequency):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(frequency)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)
        if debug:
            print( "Setting PWM frequency to %d Hz" % frequency )
            print ("Estimated pre-scale: %d" % prescaleval )

            print ("Final pre-scale: %d" % prescale)

        oldmode = self.readU8(self.__MODE1);
        #
        # go to sleep
        #
        newmode = (oldmode & 0x7F) | 0x10             # no reset, sleep
        self.write8(self.__MODE1, newmode)        # go to sleep

        self.write8(self.__PRE_SCALE, int(math.floor(prescale)))
        #
        # leave sleep
        #
        self.write8(self.__MODE1, oldmode)
        #
        # this time is NOT in the database
        #
        time.sleep(0.005)
        self.write8(self.__MODE1, oldmode | 0x80)

    def _setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write8(self.__LED0_ON_L + 4*channel, on & 0xFF)
        self.write8(self.__LED0_ON_H + 4*channel, on >> 8)

        self.write8(self.__LED0_OFF_L + 4*channel, off & 0xFF)
        self.write8(self.__LED0_OFF_H + 4*channel, off >> 8)

    def _reset(self):
        self.write8(self.__MODE1, 0x00)

    def channel_0(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(0, value)

    def channel_1(self, value):
        self._channel(1, value)

    def channel_2(self, value):
        self._channel(2, value)

    def channel_3(self, value):
        self._channel(3, value)

    def channel_4(self, value):
        self._channel(4, value)

    def channel_5(self, value):
        self._channel(5, value)

    def channel_6(self, value):
        self._channel(6, value)

    def channel_7(self, value):
        self._channel(7, value)

    def channel_8(self, value):
        self._channel(8, value)

    def channel_9(self, value):
        self._channel(9, value)

    def channel_10(self, value):
        self._channel(10, value)

    def channel_11(self, value):
        self._channel(11, value)

    def channel_12(self, value):
        self._channel(12, value)

    def channel_13(self, value):
        self._channel(13, value)

    def channel_14(self, value):
        self._channel(14, value)

    def channel_15(self, value):
        self._channel(15, value)


    def _channel(self, channel, value):
        try:
            v = float(value)
        except ValueError:
            return
        if v < 0.0 :
            v = 0.0
        if v > 100.0 :
            v = 100.0

        bv = (0xfff-1) / 100.0 * v
        self._setPWM(channel, 0, int(bv))


    """input from scratch to adapter, value = 0..servo_scale"""

    def servo_0(self, value):
        self._servo(0, value)

    def servo_1(self, value):
        self._servo(1, value)

    def servo_2(self, value):
        self._servo(2, value)

    def servo_3(self, value):
        self._servo(3, value)

    def servo_4(self, value):
        self._servo(4, value)

    def servo_5(self, value):
        self._servo(5, value)

    def servo_6(self, value):
        self._servo(6, value)

    def servo_7(self, value):
        self._servo(7, value)

    def servo_8(self, value):
        self._servo(8, value)

    def servo_9(self, value):
        self._servo(9, value)

    def servo_10(self, value):
        self._servo(10, value)

    def servo_11(self, value):
        self._servo(11, value)

    def servo_12(self, value):
        self._servo(12, value)

    def servo_13(self, value):
        self._servo(13, value)

    def servo_14(self, value):
        self._servo(14, value)

    def servo_15(self, value):
        self._servo(15, value)


    def servo_min(self, value):
        """input from scratch to adapter value in mSec"""
        self.K_servo_min = value

    def servo_max(self, value):
        """input from scratch to adapter, value in mSec"""
        self.K_servo_max = value

    def servo_scale(self, value):
        """input from scratch to adapter, value  in degrees"""
        self.K_servo_scale = value

    def _servo(self, channel, value):
        K_servo_min = float(self.K_servo_min) / (self.frequency * 0.4)  # map mSec value to 0.0-1.0
        K_servo_max = float(self.K_servo_max) / (self.frequency * 0.4)
        K_servo_scale = float(self.K_servo_scale)

        try:
            v = float(value)
        except TypeError:
            return
        if v < 0.0 :
            v = 0.0
        if v > K_servo_scale :
            v = K_servo_scale

        bv = (0xfff-1) * ( K_servo_min + ( K_servo_max - K_servo_min) / K_servo_scale * v )

        self._setPWM(channel, 0, int(bv))


# --------------------------------------------------------------------------------------
class PWM_SN3218 (adapter.adapters.I2CAdapter):
    """18 channel, 8-bit PWM I2C-bus LED controller
       PIGLOW board from pimoroni"""

    __SHUTDOWN           = 0x00
    __LED_00             = 0x01
    __LED_01             = 0x02
    __LED_02             = 0x03
    __LED_03             = 0x04
    __LED_04             = 0x05
    __LED_05             = 0x06
    __LED_06             = 0x07
    __LED_07             = 0x08
    __LED_08             = 0x09
    __LED_09             = 0x0a
    __LED_0A             = 0x0b
    __LED_0B             = 0x0c
    __LED_0C             = 0x0d
    __LED_0D             = 0x0e
    __LED_0E             = 0x0f
    __LED_0F             = 0x10
    __LED_10             = 0x11
    __LED_11             = 0x12

    __LED_CTRL_1         = 0x13
    __LED_CTRL_2         = 0x14
    __LED_CTRL_3         = 0x15

    __UPDATE             = 0x16
    __RESET              = 0x17



    mandatoryParameters = {
                           'i2c.bus' : '1',
                           'i2c.address' :'0x40'

                          }

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self)


    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up SPI
        #
        adapter.adapters.I2CAdapter.setActive(self, state)
        if state:
            self._active()


    def run(self):
        pass


    def _setPWM(self, channel, on):
        "Sets a single PWM channel"
        self.write8(self.__LED_00+channel, on & 0xFF)
        self.write8(self.__UPDATE, 0)

    def _active(self):

        self.write8(self.__SHUTDOWN,   0b00000001)
        self.write8(self.__LED_CTRL_1, 0b00111111)
        self.write8(self.__LED_CTRL_2, 0b00111111)
        self.write8(self.__LED_CTRL_3, 0b00111111)
        self.write8(self.__UPDATE, 0)

    def channel_00(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(0, value)

    def channel_01(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(1, value)

    def channel_02(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(2, value)

    def channel_03(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(3, value)

    def channel_04(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(4, value)

    def channel_05(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(5, value)

    def channel_06(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(6, value)

    def channel_07(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(7, value)

    def channel_08(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(8, value)

    def channel_09(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(9, value)

    def channel_0A(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(10, value)

    def channel_0B(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(11, value)

    def channel_0C(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(12, value)

    def channel_0D(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(13, value)

    def channel_0E(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(14, value)

    def channel_0F(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(15, value)

    def channel_10(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(16, value)

    def channel_11(self, value):
        """input from scratch to adapter, value = 0..100"""
        self._channel(17, value)

    def _channel(self, channel, value):
        try:
            v = float(value)
        except TypeError:
            return
        if v < 0.0 :
            v = 0.0
        if v > 100.0 :
            v = 100.0

        bv = 0xff / 100.0 * v
        self._setPWM(channel, int(bv))

# --------------------------------------------------------------------------------------
class ADC_DAC_PCF8591 (adapter.adapters.I2CAdapter):
    """4-channel ADC, 1 Channel DAC"""

    mandatoryParameters = {
                           'i2c.bus' : '1',
                           'i2c.address' :'0x48',
                           'dac.enable': 'false',
                           'poll.interval': '0.1'
                          }

    optionalParameters = {
                            'average.enable': 'false',
                            'average.cnt': '4'
                        }

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self)
        self._dac = 0

    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up I2C
        #
        adapter.adapters.I2CAdapter.setActive(self, state)

    def run(self):
        _del = float( self.parameters['poll.interval'] )
        self._dac_enabled = self.isTrue( self.parameters['dac.enable'] )


        average_enable = self.isTrue( self.parameters.get( 'average.enable', 'false' ) )
        average_cnt = int ( self.parameters.get( 'average.cnt', '5' ) )
        if average_cnt == 0:
            average_cnt = 2

        if self._dac_enabled:
            self._enableDAC()
        else:
            self._disableDAC()

        last = [ None, None, None, None ]
        average = [ 0, 0, 0, 0 ]
        average_state = 0

        while not self.stopped():
            self.delay(_del)

            current = self._readAllADC()

            if average_enable:
                for i in range(4):
                    average[i] = average[i] + current[i]
                average_state  += 1

                if average_state >= average_cnt:
                    for i in range(4):
                        average[i] = average[i] / average_cnt

                    self._send_adc_array( last, average )
                    average = [ 0, 0, 0, 0 ]
                    average_state = 0
            else:
                self._send_adc_array( last, current )

            if self._dac_enabled:
                self._writeDAC(self._dac)

    def _send_adc_array(self, last, current):
        for i in range(4):
            if  current[i] != last[i]:
                last[i] = current[i]
                if i == 0:
                    self.adc_0 ( current[i] )
                if i == 1:
                    self.adc_1 ( current[i] )
                if i == 2:
                    self.adc_2 ( current[i] )
                if i == 3:
                    self.adc_3 ( current[i] )

    def adc_0(self, value):
        self.sendValue(value)

    def adc_1(self, value):
        self.sendValue(value)

    def adc_2(self, value):
        self.sendValue(value)

    def adc_3(self, value):
        self.sendValue(value)

    def dac(self, value):
        """input from scratch to adapter, value = 0..255"""
        v = float(value)
        if v < 0.0:
            v = 0.0
        if v > 255.0:
            v = 255.0

        vi = int(v)
        self._dac = vi

    # Read single ADC Channel
    def _readADC(self, __chan = 0):
        __checkedChan = self.__checkChannelNo(__chan)

        self.__bus.write_byte(self.__addr, 0x40 | __checkedChan & 0x03)  # mod my Max - says it more reliable
#       self.__bus.write_byte(self.__addr, __checkedChan  | self.__DACEnabled)

        __reading = self.__bus.read_byte(self.__addr) # seems to need to throw away first reading
        __reading = self.__bus.read_byte(self.__addr) # read A/D
        return __reading

    # Read all ADC channels
    def _readAllADC(self):
        __readings = []
        AUTO_INCREMENT = 0x04
        DAC_ENABLE = 0x40
        if self._dac_enabled:
            cmd = DAC_ENABLE | AUTO_INCREMENT
        else:
            cmd = AUTO_INCREMENT

        __readings = self.readList(cmd, 5)
        __readings = __readings[1:]
        return __readings

    # Set DAC value and enable output
    def _writeDAC(self, __val=0):
#        self.__DACEnabled = 0x40
#        self.__bus.write_byte_data(self.__addr, self.__DACEnabled, __checkedVal)
        DAC_ENABLE = 0x40
        self.write8(DAC_ENABLE, __val )

    # Enable DAC output
    def _enableDAC(self):
        DAC_ENABLE = 0x40
        self.write8( DAC_ENABLE, 0 )

    # Disable DAC output
    def _disableDAC(self):
        DACDisabled = 0x00
        self.write8( DACDisabled, 0 )

# --------------------------------------------------------------------------------------
# The MPR121 Adapter is based on code from adafruit.com
#
class MPR121_Channel():
    # pylint: disable=protected-access
    """Helper class to represent a touch channel on the MPR121. Not meant to
    be used directly."""
    def __init__(self, mpr121, channel):
        self._mpr121 = mpr121
        self._channel = channel

    @property
    def value(self):
        """Whether the touch pad is being touched or not."""
        return self._mpr121.touched() & (1 << self._channel) != 0

    @property
    def raw_value(self):
        """The raw touch measurement."""
        return self._mpr121.filtered_data(self._channel)

    @property
    def threshold(self):
        """The touch threshold."""
        buf = bytearray(1)
        self._mpr121._read_register_bytes(Touch_MPR121.MPR121_TOUCHTH_0 + 2*self._channel, buf, 1)
        return buf[0]

    @threshold.setter
    def threshold(self, value):
        self._mpr121._write_register_byte(Touch_MPR121.MPR121_TOUCHTH_0 + 2*self._channel, value)

    @property
    def release_threshold(self):
        """The release threshold."""
        buf = bytearray(1)
        self._mpr121._read_register_bytes(Touch_MPR121.MPR121_RELEASETH_0 + 2*self._channel, buf, 1)
        return buf[0]

    @release_threshold.setter
    def release_threshold(self, value):
        self._mpr121._write_register_byte(Touch_MPR121.MPR121_RELEASETH_0 + 2*self._channel, value)


class Touch_MPR121(adapter.adapters.I2CAdapter):
    """Driver for the MPR121 capacitive touch breakout board."""

    # Register addresses.  Unused registers commented out to save memory.
    # pylint: disable=bad-whitespace
    MPR121_I2CADDR_DEFAULT = 0x5A
    MPR121_TOUCHSTATUS_L   = 0x00
    # MPR121_TOUCHSTATUS_H   = 0x01
    MPR121_FILTDATA_0L     = 0x04
    # MPR121_FILTDATA_0H     = 0x05
    MPR121_BASELINE_0      = 0x1E
    MPR121_MHDR            = 0x2B
    MPR121_NHDR            = 0x2C
    MPR121_NCLR            = 0x2D
    MPR121_FDLR            = 0x2E
    MPR121_MHDF            = 0x2F
    MPR121_NHDF            = 0x30
    MPR121_NCLF            = 0x31
    MPR121_FDLF            = 0x32
    MPR121_NHDT            = 0x33
    MPR121_NCLT            = 0x34
    MPR121_FDLT            = 0x35
    MPR121_TOUCHTH_0       = 0x41
    MPR121_RELEASETH_0     = 0x42
    MPR121_DEBOUNCE        = 0x5B
    MPR121_CONFIG1         = 0x5C
    MPR121_CONFIG2         = 0x5D
    # MPR121_CHARGECURR_0    = 0x5F
    # MPR121_CHARGETIME_1    = 0x6C
    MPR121_ECR             = 0x5E
    # MPR121_AUTOCONFIG0     = 0x7B
    # MPR121_AUTOCONFIG1     = 0x7C
    # MPR121_UPLIMIT         = 0x7D
    # MPR121_LOWLIMIT        = 0x7E
    # MPR121_TARGETLIMIT     = 0x7F
    # MPR121_GPIODIR         = 0x76
    # MPR121_GPIOEN          = 0x77
    # MPR121_GPIOSET         = 0x78
    # MPR121_GPIOCLR         = 0x79
    # MPR121_GPIOTOGGLE      = 0x7A
    MPR121_SOFTRESET       = 0x80
    # pylint: enable=bad-whitespace

    mandatoryParameters = { 'poll.interval': '0.1',
                           'i2c.bus' : '1',

                            # ADDR not connected: 0x5A
                            # ADDR tied to 3V: 0x5B
                            # ADDR tied to SDA: 0x5C
                            # ADDR tied to SCL: 0x5D

                           'i2c.address' :'0x5a'
                          }

    def __init__(self):
        adapter.adapters.I2CAdapter.__init__(self)
        self._buffer = bytearray(2)
        self._channels = [None]*12


    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up adapter
        #
        adapter.adapters.I2CAdapter.setActive(self, state);

    def run(self):
        if debug:
            print(self.name, "run()")

        self.reset()

        _del = float(self.parameters['poll.interval'])

        #
        # tf, ef are arrays of functions
        #
        tf = []
        tf.append( self.touch_00 )
        tf.append( self.touch_01 )
        tf.append( self.touch_02 )
        tf.append( self.touch_03 )
        tf.append( self.touch_04 )
        tf.append( self.touch_05 )
        tf.append( self.touch_06 )
        tf.append( self.touch_07 )
        tf.append( self.touch_08 )
        tf.append( self.touch_09 )
        tf.append( self.touch_10 )
        tf.append( self.touch_11 )

        ef = []
        ef.append( self.event_00 )
        ef.append( self.event_01 )
        ef.append( self.event_02 )
        ef.append( self.event_03 )
        ef.append( self.event_04 )
        ef.append( self.event_05 )
        ef.append( self.event_06 )
        ef.append( self.event_07 )
        ef.append( self.event_08 )
        ef.append( self.event_09 )
        ef.append( self.event_10 )
        ef.append( self.event_11 )

        last = self.touched()

        for i in range(12):
            mask = 1 << i

            if (last & mask ) :
                tf[i] ( 1 )
            else:
                tf[i] ( 0 )

        while not self.stopped():
            #
            self.delay(_del)
            current = self.touched()
            if debug:
                print("{c:5d} {c:012b}   {c2:04b} {c1:04b} {c0:04b}".format( c = current,
                                                                c2 = ((current >> 8) & 0xf),
                                                                c1 = ((current >> 4) & 0xf),
                                                                c0 = ((current >> 0) & 0xf) ) )
            for i in range(12):
                mask = 1 << i

                if (last & mask ) != (current & mask ):
                    if current & mask > 0:
                        ef[i] ()
                        tf[i] ( 1 )
                    else:
                        tf[i] ( 0 )

            last = current

    def touch_00(self, value):  self.sendValue(value)
    def touch_01(self, value):  self.sendValue(value)
    def touch_02(self, value):  self.sendValue(value)
    def touch_03(self, value):  self.sendValue(value)
    def touch_04(self, value):  self.sendValue(value)
    def touch_05(self, value):  self.sendValue(value)
    def touch_06(self, value):  self.sendValue(value)
    def touch_07(self, value):  self.sendValue(value)
    def touch_08(self, value):  self.sendValue(value)
    def touch_09(self, value):  self.sendValue(value)
    def touch_10(self, value):  self.sendValue(value)
    def touch_11(self, value):  self.sendValue(value)

    def event_00(self):  self.send()
    def event_01(self):  self.send()
    def event_02(self):  self.send()
    def event_03(self):  self.send()
    def event_04(self):  self.send()
    def event_05(self):  self.send()
    def event_06(self):  self.send()
    def event_07(self):  self.send()
    def event_08(self):  self.send()
    def event_09(self):  self.send()
    def event_10(self):  self.send()
    def event_11(self):  self.send()

    def __getitem__(self, key):
        if key < 0 or key > 11:
            raise IndexError('Pin must be a value 0-11.')
        if self._channels[key] is None:
            self._channels[key] = MPR121_Channel(self, key)
        return self._channels[key]

    @property
    def touched_pins(self):
        """A tuple of touched state for all pins."""
        touched = self.touched()
        return tuple([bool(touched >> i & 0x01) for i in range(12)])

    def _write_register_byte(self, register, value):
        # Write a byte value to the specifier register address.
        # MPR121 must be put in Stop Mode to write to most registers
        stop_required = True
        if register == Touch_MPR121.MPR121_ECR or 0x73 <= register <= 0x7A:
            stop_required = False
        #with self._i2c:
        #    if stop_required:
        #        self._i2c.write(bytes([Touch_MPR121.MPR121_ECR, 0x00]))
        #    self._i2c.write(bytes([register, value]))
        #    if stop_required:
        #        self._i2c.write(bytes([Touch_MPR121.MPR121_ECR, 0x8F]))

        if stop_required:
            self.write8( Touch_MPR121.MPR121_ECR, 0x00 )

        self.write8( register, value )

        if stop_required:
            self.write8( Touch_MPR121.MPR121_ECR,  0x8F  )

    def _read_register_bytes(self, register, result, length=None):
        # Read the specified register address and fill the specified result byte
        # array with result bytes.  Make sure result buffer is the desired size
        # of data to read.
        if length is None:
            length = len(result)
        #with self._i2c:
        #    self._i2c.write_then_readinto(bytes([register]), result,
        #                                  in_end=length, stop=False)
        self.writeList( register, [] )
        self.readList( register, length)

    def reset(self):
        """Reset the MPR121 into a default state ready to detect touch inputs.
        """
        # Write to the reset register.
        self._write_register_byte(Touch_MPR121.MPR121_SOFTRESET, 0x63)
        time.sleep(0.001) # This 1ms delay here probably isn't necessary but can't hurt.
        # Set electrode configuration to default values.
        self._write_register_byte(Touch_MPR121.MPR121_ECR, 0x00)

        # Check CDT, SFI, ESI configuration is at default values.
        ## self._read_register_bytes(Touch_MPR121.MPR121_CONFIG2, self._buffer, 1)
        self._buffer = self.readList(Touch_MPR121.MPR121_CONFIG2, 2)

        if debug:
            print("buffer",  self._buffer )

        if self._buffer[0] != 0x24:
            raise RuntimeError('Failed to find MPR121 in expected config state!')
        # Default touch and release thresholds
        for i in range(12):
            self._write_register_byte(Touch_MPR121.MPR121_TOUCHTH_0 + 2*i, 12)
            self._write_register_byte(Touch_MPR121.MPR121_RELEASETH_0 + 2*i, 6)
        # Configure baseline filtering control registers.
        self._write_register_byte(Touch_MPR121.MPR121_MHDR, 0x01)
        self._write_register_byte(Touch_MPR121.MPR121_NHDR, 0x01)
        self._write_register_byte(Touch_MPR121.MPR121_NCLR, 0x0E)
        self._write_register_byte(Touch_MPR121.MPR121_FDLR, 0x00)
        self._write_register_byte(Touch_MPR121.MPR121_MHDF, 0x01)
        self._write_register_byte(Touch_MPR121.MPR121_NHDF, 0x05)
        self._write_register_byte(Touch_MPR121.MPR121_NCLF, 0x01)
        self._write_register_byte(Touch_MPR121.MPR121_FDLF, 0x00)
        self._write_register_byte(Touch_MPR121.MPR121_NHDT, 0x00)
        self._write_register_byte(Touch_MPR121.MPR121_NCLT, 0x00)
        self._write_register_byte(Touch_MPR121.MPR121_FDLT, 0x00)
        # Set other configuration registers.
        self._write_register_byte(Touch_MPR121.MPR121_DEBOUNCE, 0)
        self._write_register_byte(Touch_MPR121.MPR121_CONFIG1, 0x10) # default, 16uA charge current
        self._write_register_byte(Touch_MPR121.MPR121_CONFIG2, 0x20) # 0.5uS encoding, 1ms period
        # Enable all electrodes.
        self._write_register_byte(Touch_MPR121.MPR121_ECR, 0x8F) # start with first 5 bits of baseline tracking

    def filtered_data(self, pin):
        """Return filtered data register value for the provided pin (0-11).
        Useful for debugging.
        """
        if pin < 0 or pin > 11:
            raise ValueError('Pin must be a value 0-11.')
        self._read_register_bytes(Touch_MPR121.MPR121_FILTDATA_0L + pin*2, self._buffer)
        return ((self._buffer[1] << 8) | (self._buffer[0])) & 0xFFFF

    def baseline_data(self, pin):
        """Return baseline data register value for the provided pin (0-11).
        Useful for debugging.
        """
        if pin < 0 or pin > 11:
            raise ValueError('Pin must be a value 0-11.')
        self._read_register_bytes(Touch_MPR121.MPR121_BASELINE_0 + pin, self._buffer, 1)
        return self._buffer[0] << 2

    def touched(self):
        """Return touch state of all pins as a 12-bit value where each bit
        represents a pin, with a value of 1 being touched and 0 not being touched.
        """
        ## self._read_register_bytes(Touch_MPR121.MPR121_TOUCHSTATUS_L, self._buffer)

        self._buffer = self.readList(Touch_MPR121.MPR121_TOUCHSTATUS_L, 2)

        return ((self._buffer[1] << 8) | (self._buffer[0])) & 0xFFFF

    def is_touched(self, pin):
        """Return True if the specified pin is being touched, otherwise returns
        False.
        """
        if pin < 0 or pin > 11:
            raise ValueError('Pin must be a value 0-11.')
        touches = self.touched()
        return (touches & (1 << pin)) > 0
