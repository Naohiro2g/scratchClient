# -*- coding: utf-8 -*-

## This adapter is provided by SFYRAKIS. 
## For installation, see the documentation.

import adapter.adapters
import logging

logger = logging.getLogger(__name__)

try:
    import gps3
    import gps3.agps3threaded
except ImportError:
    logger.error("This library requires gps3\nInstall with: sudo pip3 install gps3")

debug = False

# -------------------------------------------------------------------------------------------------------------
class GY_GPS6MV2(adapter.adapters.Adapter):

    mandatoryParameters = { 'poll.interval': 1 }
    
    def __init__(self):
        if debug:
            print("TestAdapter init")
        adapter.adapters.Adapter.__init__(self)

        
    def setActive (self, state):
        if debug:
            print(self.name, "setActive", state)
        #
        # use default implementation to start up GPIO
        #
        adapter.adapters.Adapter.setActive(self, state);

               
    def run(self):
        if debug:
            print("run in test Adapter")
        _del = float(self.parameters['poll.interval'])
        if _del < 0.02:
            _del = 0.02
        
        agps_thread = gps3.agps3threaded.AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
        agps_thread.stream_data()                          # From localhost (), or other hosts, by example, (host='gps.ddns.net')
        agps_thread.run_thread()                           # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second

        while not self.stopped():
            #
            # delay 5 sec, but break time in small junks to allow stopping fast
            #
            self.delay(_del)
            try:
                self.time  (agps_thread.data_stream.time )
                self.lat   (agps_thread.data_stream.lat  )
                self.lon   (agps_thread.data_stream.lon  )
                self.alt   (agps_thread.data_stream.alt  )
                self.speed (agps_thread.data_stream.speed)
                self.track (agps_thread.data_stream.track)
                self.epx   (agps_thread.data_stream.epx  )
                self.epy   (agps_thread.data_stream.epy  )
                self.epv   (agps_thread.data_stream.epv  )
                self.eps   (agps_thread.data_stream.eps  )
            except KeyError:
                pass
            # except KeyboardInterrupt:
            #        quit()
            except StopIteration:
                
                logger.warn (self.name + ": GPSD has terminated")
                break
        agps_thread.stop()
        
    def time(self, value):
        # receives measured time in microseconds, sends seconds towards scratch
        if debug:
            print("time", value)
        self.sendValue(value)


    def lat(self, value):
        # receives the Latitude value and send it to scratch client
        if debug:
            print("Latitude", value)
        self.sendValue(value)

    def lon(self, value):
        #receives the Longitude value and send it to scratch client
        if debug:
            print("Longitude", value)
        self.sendValue(value)

    def alt(self, value):
        # receives the Altitude value and send it to scratch client
        if debug:
            print("Altitude", value)
        self.sendValue(value)

    def speed(self, value):
        # receives the Speed  value and send it to scratch client
        if debug:
            print("Speed", value)
        self.sendValue(value)


    def track(self, value):
        # receives the Course  value and send it to scratch client
        if debug:
            print("Track", value)
        self.sendValue(value)


    def epx(self, value):
        # receives the Latitude Error value and send it to scratch client
        if debug:
            print("Epx, Latitude Error", value)
        self.sendValue(value)

    def epy(self, value):
        # receives the Longitude Error value and send it to scratch client
        if debug:
            print("Epy, Longitude Error", value)
        self.sendValue(value)

    def epv(self, value):
        # receives the Altitude Error value and send it to scratch client
        if debug:
            print("Epv, Altitude Error", value)
        self.sendValue(value)

    def eps(self, value):
        # receives the Speed Error value and send it to scratch client
        if debug:
            print("Eps, Speed Error", value)
        self.sendValue(value)

