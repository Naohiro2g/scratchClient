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
import re

debug = False

class Font_5_7:
    """ Font created at init-time from readable patterns"""
    font_5_7 = {}
    
    font_5_7[ u' '] = """
          :     :
          :     :
          :     :
          :     :
          :     :
          :     :
          :     :
    """
    font_5_7[ u'!'] = """
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :     :
          :  *  :
    """
    font_5_7[ u'"'] = """
          : * * :
          : * * :
          : * * :
          :     :
          :     :
          :     :
          :     :
    """
    font_5_7[ u'#'] = """
          : * * :
          : * * :
          :*****:
          : * * :
          :*****:
          : * * :
          : * * :
    """
    font_5_7[ u'$'] = """
          :  *  :
          : ****:
          :* *  :
          : *** :
          :  * *:
          :**** :
          :  *  :
    """
    font_5_7[ u'則'] = """
          :  ** :
          : *   :
          :  *  :
          : * * :
          :  *  :
          :   * :
          : **  :
    """
    font_5_7[ u'%'] = """
          :**   :
          :**  *:
          :   * :
          :  *  :
          : *   :
          :*  **:
          :   **:
    """
    font_5_7[ u'&'] = """
          : **  :
          :*  * :
          :* *  :
          : *   :
          :* * *:
          :*  * :
          : ** *:
    """
    font_5_7[ "'"] = """
          : **  :
          :  *  :
          : *   :
          :     :
          :     :
          :     :
          :     :
    """
    font_5_7[ u'('] = """
          :   * :
          :  *  :
          : *   :
          : *   :
          : *   :
          :  *  :
          :   * :
    """
    font_5_7[ u')'] = """
          : *   :
          :  *  :
          :   * :
          :   * :
          :   * :
          :  *  :
          : *   :
    """
    font_5_7[ u'*'] = """
          :     :
          : * * :
          :  *  :
          :*****:
          :  *  :
          : * * :
          :     :
    """
    font_5_7[ u'+'] = """
          :     :
          :  *  :
          :  *  :
          :*****:
          :  *  :
          :  *  :
          :     :
    """
    font_5_7[ u','] = """
          :     :
          :     :
          :     :
          :     :
          : **  :
          :  *  :
          : *   :
    """
    font_5_7[ u'-'] = """
          :     :
          :     :
          :     :
          :*****:
          :     :
          :     :
          :     :
    """
    font_5_7[ u'.'] = """
          :     :
          :     :
          :     :
          :     :
          :     :
          : **  :
          : **  :
    """
    font_5_7[ u'/'] = """
          :     :
          :    *:
          :   * :
          :  *  :
          : *   :
          :*    :
          :     :
    """
    font_5_7[ u'0'] = """
          : *** :
          :*   *:
          :*  **:
          :* * *:
          :**  *:
          :*   *:
          : *** :
    """
    font_5_7[ u'1'] = """
          :  *  :
          : **  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          : *** :
    """
    font_5_7[ u'2'] = """
          : *** :
          :*   *:
          :    *:
          :   * :
          :  *  :
          : *   :
          :*****:
    """
    font_5_7[ u'3'] = """
          :*****:
          :   * :
          :  *  :
          :   * :
          :    *:
          :*   *:
          : *** :
    """
    font_5_7[ u'4'] = """
          :   * :
          :  ** :
          : * * :
          :*  * :
          :*****:
          :   * :
          :   * :
    """
    font_5_7[ u'5'] = """
          :*****:
          :*    :
          :**** :
          :    *:
          :    *:
          :*   *:
          : *** :
    """
    font_5_7[ u'6'] = """
          :  ** :
          : *   :
          :*    :
          :**** :
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'7'] = """
          :*****:
          :    *:
          :   * :
          :  *  :
          : *   :
          : *   :
          : *   :
    """
    font_5_7[ u'8'] = """
          : *** :
          :*   *:
          :*   *:
          : *** :
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'9'] = """
          : *** :
          :*   *:
          :*   *:
          : ****:
          :    *:
          :   * :
          : **  :
    """
    font_5_7[ u':'] = """
          :     :
          : **  :
          : **  :
          :     :
          : **  :
          : **  :
          :     :
    """
    font_5_7[ u';'] = """
          :     :
          : **  :
          : **  :
          :     :
          : **  :
          :  *  :
          : *   :
    """
    font_5_7[ u'<'] = """
          :    *:
          :   * :
          :  *  :
          : *   :
          :  *  :
          :   * :
          :    *:
    """
    font_5_7[ u'='] = """
          :     :
          :     :
          :*****:
          :     :
          :*****:
          :     :
          :     :
    """
    font_5_7[ u'>'] = """
          :*    :
          : *   :
          :  *  :
          :   * :
          :  *  :
          : *   :
          :*    :
    """
    font_5_7[ u'?'] = """
          : *** :
          :*   *:
          :    *:
          :   * :
          :  *  :
          :     :
          :  *  :
    """
    font_5_7[ u'@'] = """
          : *** :
          :*   *:
          :    *:
          : ** *:
          :* * *:
          :* * *:
          : *** :
    """
    font_5_7[ u'A'] = """
          : *** :
          :*   *:
          :*   *:
          :*   *:
          :*****:
          :*   *:
          :*   *:
    """
    font_5_7[ u'Ä'] = """
          :*   *:
          : *** :
          :*   *:
          :*   *:
          :*****:
          :*   *:
          :*   *:
    """
    font_5_7[ u'B'] = """
          :**** :
          :*   *:
          :*   *:
          :**** :
          :*   *:
          :*   *:
          :**** :
    """
    font_5_7[ u'C'] = """
          : *** :
          :*   *:
          :*    :
          :*    :
          :*    :
          :*   *:
          : *** :
    """
    font_5_7[ u'D'] = """
          :***  :
          :*  * :
          :*   *:
          :*   *:
          :*   *:
          :*  * :
          :***  :
    """
    font_5_7[ u'E'] = """
          :*****:
          :*    :
          :*    :
          :**** :
          :*    :
          :*    :
          :*****:
    """
    font_5_7[ u'F'] = """
          :*****:
          :*    :
          :*    :
          :***  :
          :*    :
          :*    :
          :*    :
    """
    font_5_7[ u'G'] = """
          : *** :
          :*   *:
          :*    :
          :*    :
          :*  **:
          :*   *:
          : *** :
    """
    font_5_7[ u'H'] = """
          :*   *:
          :*   *:
          :*   *:
          :*****:
          :*   *:
          :*   *:
          :*   *:
    """
    font_5_7[ u'I'] = """
          : *** :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          : *** :
    """
    font_5_7[ u'J'] = """
          :  ***:
          :   * :
          :   * :
          :   * :
          :   * :
          :*  * :
          : **  :
    """
    font_5_7[ u'K'] = """
          :*   *:
          :*  * :
          :* *  :
          :**   :
          :* *  :
          :*  * :
          :*   *:
    """
    font_5_7[ u'L'] = """
          :*    :
          :*    :
          :*    :
          :*    :
          :*    :
          :*    :
          :*****:
    """
    font_5_7[ u'M'] = """
          :*   *:
          :** **:
          :* * *:
          :*   *:
          :*   *:
          :*   *:
          :*   *:
    """
    font_5_7[ u'N'] = """
          :*   *:
          :*   *:
          :**  *:
          :* * *:
          :*  **:
          :*   *:
          :*   *:
    """
    font_5_7[ u'O'] = """
          : *** :
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'Ö'] = """
          :*   *:
          : *** :
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'P'] = """
          :**** :
          :*   *:
          :*   *:
          :**** :
          :*    :
          :*    :
          :*    :
    """
    font_5_7[ u'Q'] = """
          : *** :
          :*   *:
          :*   *:
          :*   *:
          :* * *:
          :*  * :
          : ** *:
    """
    font_5_7[ u'R'] = """
          :**** :
          :*   *:
          :*   *:
          :**** :
          :* *  :
          :*  * :
          :*   *:
    """
    font_5_7[ u'S'] = """
          : ****:
          :*    :
          :*    :
          : *** :
          :    *:
          :    *:
          :**** :
    """
    font_5_7[ u'T'] = """
          :*****:
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
    """
    font_5_7[ u'U'] = """
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'Ü'] = """
          :*   *:
          :     :
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'V'] = """
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          :*   *:
          : * * :
          :  *  :
    """
    font_5_7[ u'W'] = """
          :*   *:
          :*   *:
          :*   *:
          :* * *:
          :* * *:
          :** **:
          :*   *:
    """
    font_5_7[ u'X'] = """
          :*   *:
          :*   *:
          : * * :
          :  *  :
          : * * :
          :*   *:
          :*   *:
    """
    font_5_7[ u'Y'] = """
          :*   *:
          :*   *:
          : * * :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
    """
    font_5_7[ u'Ý'] = """
          :   * :
          :* * *:
          :*   *:
          : * * :
          :  *  :
          :  *  :
          :  *  :
    """
    font_5_7[ u'Z'] = """
          :*****:
          :    *:
          :   * :
          :  *  :
          : *   :
          :*    :
          :*****:
    """
    font_5_7[ u'['] = """
          :  ***:
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  ***:
    """
    font_5_7[ u'\\'] = """
          :     :
          :*    :
          : *   :
          :  *  :
          :   * :
          :    *:
          :     :
    """
    font_5_7[ u']'] = """
          :***  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :***  :
    """
    font_5_7[ u'^'] = """
          :  *  :
          : * * :
          :*   *:
          :     :
          :     :
          :     :
          :     :
    """
    font_5_7[ u'_'] = """
          :     :
          :     :
          :     :
          :     :
          :     :
          :     :
          :*****:
    """
    font_5_7[ u'`'] = """
          : *   :
          :  *  :
          :   * :
          :     :
          :     :
          :     :
          :     :
    """
    font_5_7[ u'a'] = """
          :     :
          :     :
          : *** :
          :    *:
          : ****:
          :*   *:
          : ****:
    """
    font_5_7[ u'ä'] = """
          :*   *:
          :     :
          : *** :
          :    *:
          : ****:
          :*   *:
          : ****:
    """
    font_5_7[ u'b'] = """
          :*    :
          :*    :
          :* ** :
          :**  *:
          :*   *:
          :*   *:
          :**** :
    """
    font_5_7[ u'c'] = """
          :     :
          :     :
          : *** :
          :*    :
          :*    :
          :*   *:
          : *** :
    """
    font_5_7[ u'd'] = """
          :    *:
          :    *:
          : ** *:
          :*  **:
          :*   *:
          :*   *:
          : ****:
    """
    font_5_7[ u'e'] = """
          :     :
          :     :
          : *** :
          :*   *:
          :*****:
          :*    :
          : *** :
    """
    font_5_7[ u'f'] = """
          :  ** :
          : *  *:
          : *   :
          :***  :
          : *   :
          : *   :
          : *   :
    """
    font_5_7[ u'g'] = """
          :     :
          :     :
          : ****:
          :*   *:
          : ****:
          :    *:
          :  ** :
    """
    font_5_7[ u'h'] = """
          :*    :
          :*    :
          :* ** :
          :**  *:
          :*   *:
          :*   *:
          :*   *:
    """
    font_5_7[ u'i'] = """
          :  *  :
          :     :
          : **  :
          :  *  :
          :  *  :
          :  *  :
          : *** :
    """
    font_5_7[ u'j'] = """
          :   * :
          :     :
          :  ** :
          :   * :
          :   * :
          :*  * :
          : **  :
    """
    font_5_7[ u'k'] = """
          : *   :
          : *   :
          : *  *:
          : * * :
          : **  :
          : * * :
          : *  *:
    """
    font_5_7[ u'l'] = """
          : **  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          : *** :
    """
    font_5_7[ u'm'] = """
          :     :
          :     :
          :** * :
          :* * *:
          :* * *:
          :*   *:
          :*   *:
    """
    font_5_7[ u'n'] = """
          :     :
          :     :
          :* ** :
          :**  *:
          :*   *:
          :*   *:
          :*   *:
    """
    font_5_7[ u'o'] = """
          :     :
          :     :
          : *** :
          :*   *:
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'ö'] = """
          :*   *:
          :     :
          : *** :
          :*   *:
          :*   *:
          :*   *:
          : *** :
    """
    font_5_7[ u'p'] = """
          :     :
          :     :
          :**** :
          :*   *:
          :**** :
          :*    :
          :*    :
    """
    font_5_7[ u'q'] = """
          :     :
          :     :
          : ** *:
          :*  **:
          : ****:
          :    *:
          :    *:
    """
    font_5_7[ u'r'] = """
          :     :
          :     :
          :* ** :
          :**  *:
          :*    :
          :*    :
          :*    :
    """
    font_5_7[ u's'] = """
          :     :
          :     :
          : *** :
          :*    :
          : *** :
          :    *:
          :**** :
    """
    font_5_7[ u't'] = """
          : *   :
          : *   :
          :***  :
          : *   :
          : *   :
          : *  *:
          :  ** :
    """
    font_5_7[ u'u'] = """
          :     :
          :     :
          :*   *:
          :*   *:
          :*   *:
          :*  **:
          : ** *:
    """
    
    font_5_7[ u'ü'] = """
          :*   *:
          :     :
          :*   *:
          :*   *:
          :*   *:
          :*  **:
          : ** *:
    """
    font_5_7[ u'v'] = """
          :     :
          :     :
          :*   *:
          :*   *:
          :*   *:
          : * * :
          :  *  :
    """
    font_5_7[ u'w'] = """
          :     :
          :     :
          :*   *:
          :*   *:
          :* * *:
          :* * *:
          : * * :
    """
    font_5_7[ u'x'] = """
          :     :
          :     :
          :*   *:
          : * * :
          :  *  :
          : * * :
          :*   *:
    """
    font_5_7[ u'y'] = """
          :     :
          :     :
          :*   *:
          :*   *:
          : ****:
          :    *:
          : *** :
    """
    font_5_7[ u'z'] = """
          :     :
          :     :
          :*****:
          :   * :
          :  *  :
          : *   :
          :*****:
    """
    font_5_7[ u'{'] = """
          :   * :
          :  *  :
          :  *  :
          : *   :
          :  *  :
          :  *  :
          :   * :
    """
    font_5_7[ u'|'] = """
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
          :  *  :
    """
    font_5_7[ u'}'] = """
          : *   :
          :  *  :
          :  *  :
          :   * :
          :  *  :
          :  *  :
          : *   :
    """
    font_5_7[ u'ß'] = """
          : **  :
          :*  * :
          :* *  :
          :*  * :
          :*   *:
          :*   *:
          :* ** :
    """
    font_5_7[ u'~'] = """
          :     :
          :     :
          : *  *:
          :* * *:
          :*  * :
          :     :
          :     :
    """
    font_5_7[ u'→'] = """
          :     :
          :  *  :
          :   * :
          :*****:
          :   * :
          :  *  :
          :     :
    """
    font_5_7[ u'←'] = """
          :     :
          :  *  :
          : *   :
          :*****:
          : *   :
          :  *  :
          :     :
    """
    
    font_5_7[ u'°'] = """
          : **  :
          :*  * :
          : **  :
          :     :
          :     :
          :     :
          :     :
    """
    
    font_5_7[ u'¿'] = """
          :  *  :
          :     :
          :  *  :
          :  *  :
          : *   :
          :*   *:
          : *** :
    """
    
    font_5_7[ u'�'] = """
          :     :
          :  *  :
          : *** :
          :** **:
          : *** :
          :  *  :
          :     :
    """
    def __init__(self):
        self.font = {}
        
        for f_5_7 in self.font_5_7:
            # print(f_5_7)
            t = self.font_5_7[ f_5_7]
            m = re.findall(':([ *]{5}):', t)
            
            _bytes = [0, 0, 0, 0, 0]
            
            for k in range(0,5):
                for i in range(0,7):
                    mi = m[i]
                    if mi[k:k+1] == '*':
                        _bytes[k] += (1 << i)
                               
            self.font[f_5_7] = _bytes
            
            if debug: 
                print( "font[ '{c:s}' ] = [0x{b0:02x}, 0x{b1:02x}, 0x{b2:02x}, 0x{b3:02x}, 0x{b4:02x}]".format(
                                c = f_5_7,
                                b0= _bytes[0],
                                b1= _bytes[1],
                                b2= _bytes[2],
                                b3= _bytes[3],
                                b4= _bytes[4] ) )

    def getPattern(self, char):
        if char in self.font:
            return self.font[char]
        if debug:
            print("char    :", char)
            print("charType:", type(char))
            
            print ("no font char found for ", char )
        
        return self.font[u'�']
    
    def getSizeX(self):
        return 5
    def getSizeY(self):
        return 7
    
class Font_3_5:
    """ Font created at init-time from readable patterns"""
    digit_3_5 = {}
    
    digit_3_5[ u' '] = """ 
          :   :
          :   :
          :   :
          :   :
          :   :
    """
    digit_3_5[ u'0'] = """ 
          :***:
          :* *:
          :* *:
          :* *:
          :***:
    """
    digit_3_5[ u'1'] = """ 
          :  *:
          :  *:
          :  *:
          :  *:
          :  *:
    """
    digit_3_5[ u'2'] = """ 
          :***:
          :  *:
          :***:
          :*  :
          :***:
    """
    digit_3_5[ u'3'] = """ 
          :***:
          :  *:
          :***:
          :  *:
          :***:
    """
    digit_3_5[ u'4'] = """ 
          : * :
          :*  :
          :***:
          : * :
          : * :
    """
    digit_3_5[ u'5'] = """ 
          :***:
          :*  :
          :***:
          :  *:
          :***:
    """
    digit_3_5[ u'6'] = """ 
          :*  :
          :*  :
          :***:
          :* *:
          :***:
    """
    digit_3_5[ u'7'] = """ 
          :***:
          :  *:
          : * :
          :*  :
          :*  :
    """
    digit_3_5[ u'8'] = """ 
          :***:
          :* *:
          :***:
          :* *:
          :***:
    """
    digit_3_5[ u'9'] = """ 
          :***:
          :* *:
          :***:
          :  *:
          :  *:
    """
    digit_3_5[ u'='] = """ 
          :   :
          :***:
          :   :
          :***:
          :   :
    """
    digit_3_5[ u'/'] = """ 
          :  *:
          :  *:
          : * :
          :*  :
          :*  :
    """
    digit_3_5[ u'\\'] = """ 
          :*  :
          :*  :
          : * :
          :  *:
          :  *:
    """
    digit_3_5[ u'.'] = """ 
          :   :
          :   :
          :   :
          :   :
          :  *:
    """
    digit_3_5[ u','] = """ 
          :   :
          :   :
          :   :
          :  *:
          :  *:
    """
    digit_3_5[ u';'] = """ 
          :   :
          :  *:
          :   :
          :  *:
          :  *:
    """
    digit_3_5[ u':'] = """ 
          :   :
          :   :
          :  *:
          :   :
          :  *:
    """
    digit_3_5[ u'-'] = """ 
          :   :
          :   :
          :***:
          :   :
          :   :
    """
    digit_3_5[ u'_'] = """ 
          :   :
          :   :
          :   :
          :   :
          :***:
    """
    digit_3_5[ u'+'] = """ 
          :   :
          : * :
          :***:
          : * :
          :   :
    """
    digit_3_5[ u'?'] = """ 
          :***:
          :  *:
          : * :
          :   :
          : * :
    """
    digit_3_5[ u'�'] = """
          : * :
          :***:
          :***:
          :***:
          : * :
    """
    
    def __init__(self):
        self.font = {}
        
        for d_3_5 in self.digit_3_5:
            # print(f_5_7)
            t = self.digit_3_5[ d_3_5]
            m = re.findall(':([ *]{3}):', t)
            
            _bytes = [0, 0, 0]
            
            for k in range(0,3):
                for i in range(0,5):
                    mi = m[i]
                    if mi[k:k+1] == '*':
                        _bytes[k] += (1 << i)
                               
            self.font[d_3_5] = _bytes
            
            if debug: 
                print( "font[ '{c:s}' ] = [ 0x{b0:02x}, 0x{b1:02x}, 0x{b2:02x ]".format(
                                c = d_3_5,
                                b0= _bytes[0],
                                b1= _bytes[1],
                                b2= _bytes[2]
                                 ) )

    def getPattern(self, char):
        if char in self.font:
            return self.font[char]
        if debug:
            print("char    :", char)
            print("charType:", type(char))
            
            print ("no font char found for ", char )
        
        return self.font[u'�']

    def getSizeX(self):
        return 3
    def getSizeY(self):
        return 5
