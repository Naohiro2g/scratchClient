# -*- coding: utf-8 -*-
    # --------------------------------------------------------------------------------------------
    # Copyright (C) 2018  Gerhard Hepp
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
#
import time
import threading

import logging
logger = logging.getLogger(__name__)

debug = True
# TODO complete this stuff
        
class NANOManager:
    """NANOManager for usb tty access to arduino nano which have IDENT available."""
    

    def __init__(self):
        self.lockOpenAccess = threading.Lock()
        pass
    
    def setActive(self, state):
        """called from main module, but has no function for this manager"""
        pass

    def open(self, serialDevice, serialBaud, ident = None ):
        if debug:
            print("NANOManager open()")
            
        self.lockOpenAccess.acquire()
        try:
            pass
        finally:
            self.lockOpenAccess.release()
        return None
    

    def close(self):
        """closes all connections, selective shutdowns are not implemented"""
        pass
        