# -*- coding: utf-8 -*-
    # --------------------------------------------------------------------------------------------
    # Copyright (C) 2013-2017  Gerhard Hepp
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

debug = False
debug_grid = False

import time
import os
import json
import threading
import sys 
import traceback
#import curses
#import curses.ascii
       
import tornado.ioloop
import tornado.web
import tornado.websocket
import asyncio

import mako.template
import mako.lookup
import uuid
    
import xml.etree.ElementTree as ET
import publishSubscribe

import helper

import adapter.adapters 

import logging
logger = logging.getLogger(__name__)

import scratchClient

#configuration = {'webapp2_static': { 'static_file_path': scratchClient.modulePathHandler.getScratchClientBaseRelativePath('htdocs/static') }}
commandResolver = None
#
# strange circular dependency to base module

lookup = mako.lookup.TemplateLookup(
                                    directories=[
                                          scratchClient.modulePathHandler.getScratchClientBaseRelativePath('htdocs')
                                    ], 
                                    input_encoding='utf-8', 
                                    output_encoding='utf-8',
                                    encoding_errors='replace')

# ------------------------------------------------------------------------------------------------
_runThreads = True
parentApplication = None
remote = False
scratchXHandler = None

useLocalIOloop = True
localIOloop = None

# ------------------------------------------------------------------------------------------------
# handle item-ID values throughout code

class IDManager():
    """internal use to produce unique ID for display elements"""
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.scratch_input_command_2_display = []
        self.scratch_input_value_2_display = []
        self.scratch_output_command_2_display = []
        self.scratch_output_value_2_display = []
        self.displayid = 1000
            
    def getDisplayId_scratchInputCommand (self, scratch):
        _id = str(self.displayid)
        self.scratch_input_command_2_display.append( {'name': scratch, 'id': _id} )
        self.displayid += 1
        return _id  
     
    def getDisplayId_scratchInputValue (self, scratch):
        _id = str(self.displayid)
        self.scratch_input_value_2_display.append( {'name': scratch, 'id': _id} )
        self.displayid += 1
        return _id  
     
    def getDisplayId_scratchOutputCommand (self, scratch):
        _id = str(self.displayid)
        self.scratch_output_command_2_display.append( {'name': scratch, 'id': _id} )
        self.displayid += 1
        return _id  
     
    def getDisplayId_scratchOutputValue (self, scratch):
        _id = str(self.displayid)
        self.scratch_output_value_2_display.append( {'name': scratch, 'id': _id} )
        self.displayid += 1
        return _id  
     
    def getId (self):
        _id = str(self.displayid)
        self.displayid += 1
        return _id   
    
    def getDisplayId_scratchInputCommandSummary (self):
        """return a dict with scratch names as keys; values are list of to be animated elements"""
        res = {}
        for sic2d in  self.scratch_input_command_2_display:
            sn = sic2d['name']
            ln = sic2d['id']
            if sn in res:
                res[sn].append( ln )
            else:
                res[sn] = [ ln ]
        return res   

    def getDisplayId_scratchInputValueSummary (self):
        """return a dict with scratch names as keys; values are list of to be animated elements"""
        res = {}
        for sic2d in  self.scratch_input_value_2_display:
            sn = sic2d['name']
            ln = sic2d['id']
            if sn in res:
                res[sn].append( ln )
            else:
                res[sn] = [ ln ]
        return res   

    def getDisplayId_scratchOutputCommandSummary (self):
        """return a dict with scratch names as keys; values are list of to be animated elements"""
        res = {}
        for sic2d in  self.scratch_output_command_2_display:
            sn = sic2d['name']
            ln = sic2d['id']
            if sn in res:
                res[sn].append( ln )
            else:
                res[sn] = [ ln ]
        return res   

    def getDisplayId_scratchOutputValueSummary (self):
        """return a dict with scratch names as keys; values are list of to be animated elements"""
        res = {}
        for sic2d in  self.scratch_output_value_2_display:
            sn = sic2d['name']
            ln = sic2d['id']
            if sn in res:
                res[sn].append( ln )
            else:
                res[sn] = [ ln ]
        return res   
    
idManager = IDManager()
# ------------------------------------------------------------------------------------------------
# cherrypy-Handler
    
class BaseHandler(tornado.web.RequestHandler):
    
    def render_response(self, _template, context):
#        lookup = TemplateLookup(directories=['htdocs/static',
#                                           '../htdocs/static' 
#                                           ], input_encoding='utf-8', output_encoding='utf-8',encoding_errors='replace')
        
        # Renders a template and writes the result to the response.
        
        context['debug'] = debug
        #
        # javascript needs lowecase true/false and can't use the python settings directly.
        #
        if debug: 
            context['js_debug'] = 'true' 
        else: 
            context['js_debug'] = 'false'
        
        tmpl = lookup.get_template(_template)
        tmpl.strict_undefined=True
        
        try:
            ret =  tmpl.render( ** context )
        except Exception as e:
            print("Exception !!", e)
            traceback.print_exc()
            ret="unknown"
        
        if debug: logger.debug ("rendered: %s", ret)
        self.write(ret)
    
#    def relPath(self, path):
#        p =  configuration['webapp2_static']['static_file_path'] + path
#        logger.debug("relPath %s, %s, %s", p, "pwd", os.getcwd())
#        return p#

#    def fullPath(self, path):
#        p = os.path.abspath(os.path.join( configuration['webapp2_static']['static_file_path'], path))
#        return p
    
# ------------------------------------------------------------------------------------------------
# cherrypy-Handler
class ScratchClientMain(BaseHandler):
         
    def initialize(self, additionalpaths):
        self.additionalpaths = additionalpaths
        pass
        
    def get(self):
        context = { 'additionalpaths' :self.additionalpaths }
        
        self.render_response('template/main.html', context)
        
class Usage14Handler(BaseHandler):
    """return some usage hints for scratch"""
    def get(self):
        
        list_adapter_input_command = []
        list_adapter_output_command = []
        list_adapter_input_values = []
        list_adapter_output_values = []

        for _adapter in parentApplication.config.getAdapters():
            for inp in _adapter.inputs:
                for sn in inp.scratchNames:
                    list_adapter_input_command.append( sn )

                
            for val in _adapter.input_values:
                for sn in val.scratchNames: 
                    list_adapter_input_values.append( sn)
            
            for out in _adapter.outputs:
                list_adapter_output_command.append( out.scratchNames[0] )
                
            for out in _adapter.output_values:
                list_adapter_output_values.append( out.scratchNames[0])
                
        context = {
                   'list_adapter_input_commands'  : list_adapter_input_command,
                   'list_adapter_output_commands' : list_adapter_output_command, 
                   'list_adapter_input_values'    : list_adapter_input_values ,
                   'list_adapter_output_values'   : list_adapter_output_values 
                   }
        
        return self.render_response('template/scratchUsage14.html', context)

# ------------------------------------------------------------------------------------------------
class TemplateHandler(BaseHandler):
    def initialize(self, path):
        if debug:
            print("TemplateHandler", "path", path)
        self.path = path        
        
    def get(self, file):
        context = dict()
        self.render_response( self.path + '/' + file, context)


# ------------------------------------------------------------------------------------------------
#
class ConfigHandler(BaseHandler ):
    """return the xml-config"""
    config = None
    
        
    def get(self):
        xmlConfigName = parentApplication.config.filename
        
        
        # xmlConfig = ET.tostring(parentApplication.config.tree.getroot(),  encoding='us-ascii', method='xml')
        xmlConfigInput = ET.tostring(parentApplication.config.tree.getroot(),  encoding='UTF-8', method='html')
        
        #
        # in python 2.7, there is a string array
        # in python 3.2, there is a bytes array
        
        if xmlConfigInput.__class__.__name__ == 'bytes':
            xmlConfig = xmlConfigInput.decode('UTF-8')
        else:
            
            xmlConfig = xmlConfigInput.decode('utf-8')
            
       
        
        xmlConfig= xmlConfig.replace('<', '&lt;')
        xmlConfig= xmlConfig.replace('>', '&gt;')
        xmlConfig= xmlConfig.replace('\n', '<br/>')

        context = {'configName': xmlConfigName, 'config':xmlConfig }
        
        self.render_response('template/config.html', context)
        
class ReleaseHandler(BaseHandler ):
    """return the xml-config"""
    
    def get(self):

        context = { 'version': scratchClient.version, 'changes':scratchClient.changes }
        
        return self.render_response('template/release.html', context)

# ------------------------------------------------------------------------------------------------
# cherrypy-Handler
#
class CommandHandler_InputSide(BaseHandler ):
    """Command input from web interface"""
    
    def __init__(self):
        #publishSubscribe.Pub.subscribe('input.scratch.command')
        pass
    
    def post(self, adapter='', command='somecommand'):
        logger.debug("input, command=%s", command)
        publishSubscribe.Pub.publish('input.scratch.{name:s}'.format(name=command), {'name':command})
        ## eventHandler.resolveCommand(self, adapter, command, qualifier='input')
        return "no_return"

    
class CommandHandler_OutputSide(BaseHandler ):
    """Command input from web interface"""
    
    def __init__(self):
        #publishSubscribe.Pub.subscribe('input.scratch.command')
        pass
    
    def post(self, adapter='', command='somecommand'):
        logger.debug("output, command=%s", command)
        publishSubscribe.Pub.publish('output.scratch.command', {'name':command})
        # eventHandler.resolveCommand(self, adapter, command, qualifier='output')
        return "no_return"

# ------------------------------------------------------------------------------------------------
# cherrypy-Handler
#
           
class AdaptersHandler(BaseHandler):
    """return a graphical representation of the adapter config"""

    def rectHelper(self, gg, _id=None,
                           x = 0,
                           y = 0, 
                           width=0,
                           height = 0,
                           style = ''):
            
        rect_Adapter = ET.SubElement(gg, "rect")
        if _id != None:
            rect_Adapter.set('id', str(_id) )
        rect_Adapter.set('x', str(x))
        rect_Adapter.set('y', str(y))
        rect_Adapter.set('width', str(width))
        rect_Adapter.set('height', str(height))
        rect_Adapter.set('style', style)

        return rect_Adapter

    def textHelper(self, gg,  _id = None, 
                       text='notext', 
                            x= 0,
                            y= 0,
                            style = ''):
            
            rect_AdapterName = ET.SubElement(gg, "text")
            if _id != None:
                rect_AdapterName.set('id', str(_id))
            rect_AdapterName.set('x', str(x))
            rect_AdapterName.set('y', str(y))
            rect_AdapterName.text = text
            rect_AdapterName.set('style', style)

        
    def calculateHeight(self, _adapter):
        """height in logical grid height units; depends on number of input/output, parameter etc"""
       
        l = 1 + len(_adapter.className.split('.'))
        if isinstance(_adapter,  adapter.adapters.GPIOAdapter):
            l += len( _adapter.gpios )
        
        i = 0
        o = 0
        # inputs can have multiple scratch names
        for inp in _adapter.inputs:
            ix = len( inp.scratchNames )
            i += ix
        for inp in _adapter.input_values:
            ix = len( inp.scratchNames )
            i += ix
        i += len(_adapter.parameters)
        
        # outputs are 'unique'
        o += len(_adapter.outputs)
        o += len(_adapter.output_values)
        
        
        h = max(i, o, l)
        
        return h 

    def createOnclickInputCommand(self, _id, scratch_name ):
        jScript = ''
        jScript += '{ \n' 
        jScript += '    obj = document.getElementById("{on:s}");  \n'.format(on=_id)
        jScript += '    if ( obj != null) \n' 
        jScript += '        obj.setAttribute("onclick", "click_Command(evt,\'{id:s}\' ,\'{co:s}\' , \'{sc:s}\' );");  \n'.format( id=_id, co='input.command', sc=scratch_name )
        jScript += '} \n'
        return jScript
    
    def createOnclickOutputCommand(self, _id, scratch_name):
        jScript = ''
        jScript += '{ \n' 
        jScript += '    obj = document.getElementById("{id:s}"); \n'.format(id=_id)
        jScript += '    if ( obj != null) \n' 
        jScript += '        obj.setAttribute("onclick", "click_Command(evt,\'{id:s}\' ,\'{co:s}\' , \'{sc:s}\' );");  \n'.format( id=_id, co='output.command', sc=scratch_name )
        jScript += '} \n'
        return jScript

    def createOnclickInputValue(self, objId, rectId, adapter_name, command_name):
        jScript = ''
        jScript += '{ \n' 
        #jScript += '    document.getElementById("{id:s}").setAttribute("onclick", "click_Value_input(evt, \'{rectId:s}\', \'{ad:s}\', \'{co:s}\');" ); \n'.format(id=objId, rectId=rectId, ad=adapter_name, co=command_name)
        jScript += '    document.getElementById("{id:s}").setAttribute("onclick", "click_Value_input_float(evt, \'{rectId:s}\', \'{ad:s}\', \'{co:s}\');" ); \n'.format(id=objId, rectId=rectId, ad='input.value', co=command_name)
        jScript += '} \n'
        return jScript
    
    def createOnclickOutputValue(self, objId, rectId, adapter_name, command_name):
        jScript = ''
        jScript += '{   \n' 
        #jScript += '    document.getElementById("{id:s}").setAttribute("onclick", "click_Value_output(evt, \'{rectId:s}\', \'{ad:s}\', \'{co:s}\');" ); \n'.format(id=objId, rectId=rectId, ad=adapter_name, co=command_name)
        jScript += '    document.getElementById("{id:s}").setAttribute("onclick", "click_Value_input_float(evt, \'{rectId:s}\', \'{ad:s}\', \'{co:s}\');" ); \n'.format(id=objId, rectId=rectId, ad='output.value', co=command_name)
        jScript += '}   \n'
        return jScript
    
    def get(self):
        idManager.reset()
        xmlConfigName = parentApplication.config.filename
        description = parentApplication.config.getDescription().replace('\n', '<br/>')
        
        jScript = '"use strict";   \n'
        jScript += 'let obj;         \n'
        
        list_adapter_input_command = []
        list_adapter_output_command = []
        #
        # build svn tree from adapters
        #
        # styles
        #
        textStyleDefault = 'font-size:12px;font-style:normal;font-weight:normal;line-current_height:125%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:sans-serif'
        textStyle = textStyleDefault
        
        boldTextStyleDefault = 'font-size:12px;font-style:normal;font-weight:bold;line-current_height:125%;letter-spacing:0px;word-spacing:0px;fill:#0000ff;fill-opacity:1;stroke:none;font-family:sans-serif'
        boldTextStyle = boldTextStyleDefault
        
        gpioTextStyleDefault = 'font-size:8px;font-style:normal;font-weight:normal;line-current_height:125%;letter-spacing:0px;word-spacing:0px;fill:#808080;fill-opacity:1;stroke:none;font-family:sans-serif'
        gpioTextStyle = gpioTextStyleDefault
        
        rectStyleDefault = 'fill:#e0e0e0;fill-opacity:0.52208835;stroke:#0000ff;stroke-width:1;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none'
        rectStyle = rectStyleDefault
        # make command input areas visible by slightly darker background
        commandBackgroundStyleDefault = 'fill:#e0e0e0'
        commandBackgroundStyleTest = 'fill:#808080'
        
        commandBackgroundStyle = commandBackgroundStyleDefault
        if debug:
            commandBackgroundStyle = commandBackgroundStyleTest
            
        commandBackgroundStyle2Default = 'fill:#ff0000'
        commandBackgroundStyle2 = commandBackgroundStyle2Default
        
        valueStyleDefault = 'stroke:#0000ff;stroke-width:1'
        valueStyle = valueStyleDefault
        paraLineStyleDefault = 'fill:none;stroke:#00FF00;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1'
        paraLineStyle = paraLineStyleDefault
        
        inputLineStyleDefault = 'fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1'
        inputLineStyle = inputLineStyleDefault
        
        helperLineStyleDefault = 'fill:none;stroke:#303030;stroke-width:2px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1'
        helperLineStyle = helperLineStyleDefault
        #
        ET.register_namespace('', 'http://www.w3.org/2000/svg' )
        svg = ET.Element("{http://www.w3.org/2000/svg}svg")
        g = ET.SubElement(svg, "g")


        column_10 =  1
        column_20 = 120
        column_20_parameter = 80
            # parameter und Werteeingabe
        column_30 = 220
            # Linie Eingang
        column_40 = 340
            # Adapter
        column_50 = 460
            # output line    
        column_60 = 580
            # output values
        column_70 = 680
        column_80 = 800
        column_90 = 820
         
        # absolute current_height used so far
        current_height = 1 # top margin
        vSpacing = 20
        vGap = 4
        
        if debug_grid:
            # display a grid
            grid = {'c10' : column_10, 
                    'c20' : column_20, 
                    'c30' : column_30, 
                    'c40' : column_40, 
                    'c50' : column_50, 
                    'c60' : column_60, 
                    'c70' : column_70, 
                    'c80' : column_80, 
                    'c90' : column_90,
                    'c20p': column_20_parameter }
            
            for n in grid:
                x = grid[n]
                line_Val = ET.SubElement(g, "line")
                line_Val.set('x1', str(x) )
                line_Val.set('x2', str(x) )
                line_Val.set('y1', str(current_height) )
                line_Val.set('y2', str(current_height+vSpacing) )
                line_Val.set('style', helperLineStyle )
                
                self.textHelper( g,  text= n, 
                            x= x+5 ,
                            y= current_height +vSpacing,
                            style = boldTextStyle)
      
            current_height += vSpacing

        for _adapter in parentApplication.config.getAdapters():
            gg = ET.SubElement(g, "g")
            
            h = self.calculateHeight(_adapter)
            inside_box_lines = 0
            a = self.rectHelper(gg, _id='adapter' + '_' + _adapter.name,
                           x = column_40,
                           y = current_height, 
                           width=column_50-column_40,
                           height = h * vSpacing + vSpacing,
                           style = rectStyle)
            
            t = ET.SubElement(a, 'title')
            t.text=_adapter.description
    
            self.textHelper(gg,  text=_adapter.name, 
                            x= column_40 + 5,
                            y= current_height +  (inside_box_lines +1) * vSpacing,
                            style = boldTextStyle)
            
            inside_box_lines += 1
            # print the class name in multiple lines
            #
            class_segments = _adapter.className.split('.')
            
            for i in range( len(class_segments) ):
                s = class_segments[i]
                self.textHelper(gg,  text=s, 
                                x= column_40 + 5,
                                y= current_height +  (inside_box_lines +1) * vSpacing,
                                style = textStyle)
                inside_box_lines += 1
                
            if isinstance(_adapter,  adapter.adapters.GPIOAdapter):
                gi = 1
                for gpio in _adapter.gpios:
                    
                    atext = ''
                    if gpio.alias == None:
                        atext = "[{num:02d}] {name:s}".format(name=gpio.port, num=gpio.portNumber)
                    else:
                        atext = "[{num:02d}] {name:s} ({alias:s})".format(name=gpio.port, num=gpio.portNumber, alias=gpio.alias)
                        
                    self.textHelper(gg,  text=atext , 
                                    x= column_40 + 5,
                                    y= current_height +  (inside_box_lines +1) * vSpacing,
                                    style = gpioTextStyle)
                    gi += 1
                    inside_box_lines += 1
                
            # leftside are the left side connectors
            leftSide = 0            
            for inp in _adapter.inputs:
                
                nCommand = 0
                for _ in range(len(inp.scratchNames)):
                    
                    _id_backanimation = idManager.getDisplayId_scratchInputCommand( inp.scratchNames[nCommand] )
                    _id_back = idManager.getId( )
                    _id_text = idManager.getId( )
                    # list_adapter_input_command .append([_id , _id + "_back"])
                    
                    jScript += self.createOnclickInputCommand(_id_text , inp.scratchNames[nCommand])
                    jScript += self.createOnclickInputCommand(_id_back , inp.scratchNames[nCommand])
                    
                    textInpBack = self.rectHelper(gg, _id=_id_back,
                           x = column_10,
                           y = current_height + (leftSide+0+nCommand) * vSpacing + vGap, 
                           width=column_20-column_10,
                           height = vSpacing-vGap,
                           style = commandBackgroundStyle)
                    
                    animate = ET.SubElement(textInpBack, "animate")
                    animate.set("id", _id_backanimation)
                    animate.set("attributeType", "CSS")
                    animate.set("attributeName", "fill") 
                    animate.set("from", "#ffffff")
                    animate.set("to", "#ff0000")
                    animate.set("dur", "0.3s");
                    
                    text_Inp_Cmd = self.textHelper(gg,  text=inp.scratchNames[nCommand], 
                                    _id = _id_text,
                                    x= column_10+5,
                                    y= current_height + (leftSide+1+nCommand) * vSpacing - vGap,
                                    style = textStyle)

                    line_Inp = ET.SubElement(gg, "line")
                    line_Inp.set('x1', str(column_10) )
                    line_Inp.set('x2', str(column_20+1) )
                    line_Inp.set('y1', str(current_height + (leftSide+1+nCommand) * vSpacing) )
                    line_Inp.set('y2', str(current_height + (leftSide+1+nCommand) * vSpacing) )
                    line_Inp.set('style', inputLineStyle )
                    
                    if nCommand > 0:
                        line_Inp = ET.SubElement(gg, "line")
                        line_Inp.set('x1', str(column_20) )
                        line_Inp.set('x2', str(column_20) )
                        line_Inp.set('y1', str(current_height + (leftSide+1+nCommand-1) * vSpacing) )
                        line_Inp.set('y2', str(current_height + (leftSide+1+nCommand-0) * vSpacing) )
                        line_Inp.set('style', inputLineStyle )
                        
                    nCommand += 1
                
                text_Inp = ET.SubElement(gg, "text")
                text_Inp.set('x', str(column_30+3))
                text_Inp.set('y', str(current_height + (leftSide+nCommand) * vSpacing - vGap))
                text_Inp.text = inp.name
                text_Inp.set('style', textStyle)
                
                line_Inp = ET.SubElement(gg, "line")
                line_Inp.set('x1', str(column_20) )
                line_Inp.set('x2', str(column_40) )
                line_Inp.set('y1', str(current_height + (leftSide+nCommand) * vSpacing) )
                line_Inp.set('y2', str(current_height + (leftSide+nCommand) * vSpacing) )
                line_Inp.set('style', inputLineStyle )
 
                leftSide += nCommand
                
            for val in _adapter.input_values:
                nValue = 0
                for _ in range(len(val.scratchNames)): 
                    _id_text = idManager.getDisplayId_scratchInputValue( val.scratchNames[nValue] )
                    _id = idManager.getId()
                
                    rect_Out = ET.SubElement(gg, "rect")
                    rect_Out.set('id', _id+'_back')
                    rect_Out.set('x', str(column_20))
                    rect_Out.set('y', str(current_height + (leftSide+0+nValue) * vSpacing + vGap ))
                    rect_Out.set('width', str(column_30-column_20))
                    rect_Out.set('height', str(vSpacing - vGap))
                    rect_Out.set('style', rectStyle)
                
                    textValue_Out = ET.SubElement(gg, "text")
                    textValue_Out.set('id', _id_text )
                    textValue_Out.set('x', str(column_20+4 ))
                    textValue_Out.set('y', str(current_height + (leftSide+1+nValue) * vSpacing - vGap))
                    textValue_Out.text = '?'
                    textValue_Out.set('style', textStyle)

                    jScript += self.createOnclickInputValue( _id_text   , _id+'_back', _adapter.name, val.scratchNames[nValue])
                    jScript += self.createOnclickInputValue( _id+'_back', _id+'_back', _adapter.name, val.scratchNames[nValue])

                    text_Val = ET.SubElement(gg, "text")
                    text_Val.set('x', str(column_10))
                    text_Val.set('y', str(current_height + (leftSide+1+nValue) * vSpacing - vGap ))
                    text_Val.text = val.scratchNames[nValue]
                    text_Val.set('style', textStyle)
                    
                    line_Val = ET.SubElement(gg, "line")
                    line_Val.set('x1', str(column_10) )
                    line_Val.set('x2', str(column_20) )
                    line_Val.set('y1', str(current_height + (leftSide+1+nValue) * vSpacing) )
                    line_Val.set('y2', str(current_height + (leftSide+1+nValue) * vSpacing) )
                    line_Val.set('style', inputLineStyleDefault )
                    
                    nValue += 1

                text_Val = ET.SubElement(gg, "text")
                text_Val.set('x', str(column_30 +4 ))
                text_Val.set('y', str(current_height + (leftSide+0+nValue) * vSpacing - vGap))
                text_Val.text = val.name
                text_Val.set('style', textStyle)
                

                line_Val = ET.SubElement(gg, "line")
                line_Val.set('x1', str(column_30) )
                line_Val.set('x2', str(column_40) )
                line_Val.set('y1', str(current_height + (leftSide+0+nValue) * vSpacing) )
                line_Val.set('y2', str(current_height + (leftSide+0+nValue) * vSpacing) )
                line_Val.set('style', inputLineStyleDefault )
 
                leftSide += nValue
                
            for para in _adapter.parameters:
                
                text_Para = ET.SubElement(gg, "text")
                text_Para.set('x', str(column_20_parameter))
                text_Para.set('y', str(current_height + (leftSide+1) * vSpacing - vGap))
                text_Para.text = para + '= ' + _adapter.parameters[para]
                text_Para.set('style', textStyle)
                
                line_Para = ET.SubElement(gg, "line")
                line_Para.set('x1', str( column_20_parameter) )
                line_Para.set('x2', str( column_40) )
                line_Para.set('y1', str(current_height + (leftSide+1) * vSpacing) )
                line_Para.set('y2', str(current_height + (leftSide+1) * vSpacing) )
                line_Para.set('style', paraLineStyle )
 
                leftSide += 1
                
            # rightside are the output connectors    
            rightSide = 0   
            
            for out in _adapter.outputs:
                
                text_Out = ET.SubElement(gg, "text")
                text_Out.set('x', str(column_50+5))
                text_Out.set('y', str(current_height + (rightSide+1) * vSpacing - vGap))
                text_Out.text = out.name
                text_Out.set('style', textStyle)
                
                _id = 'adapter_' + _adapter.name + '_' + out.scratchNames[0]
                _id_backanimation = idManager.getDisplayId_scratchOutputCommand( out.scratchNames[0] )
                   
                jScript += self.createOnclickOutputCommand(_id + "_text", out.scratchNames[0])
                jScript += self.createOnclickOutputCommand(_id + "_back", out.scratchNames[0])
                
                textInpBack = ET.SubElement(gg, "rect")
                textInpBack.set('id', _id+ '_back' )
                textInpBack.set('x', str(column_70))
                textInpBack.set('y', str(current_height + (rightSide+0) * vSpacing +  vGap))
                textInpBack.set('width', str(column_80-column_70))
                textInpBack.set('height', str(vSpacing - vGap))
                textInpBack.set('style', commandBackgroundStyle)

                animate = ET.SubElement(textInpBack, "animate")
                animate.set("id", _id_backanimation)
                animate.set("attributeType", "CSS")
                animate.set("attributeName", "fill") 
                animate.set("from", "#ffffff")
                animate.set("to", "#ff0000")
                animate.set("dur", "0.3s");
                
                text_Command = ET.SubElement(gg, "text")
                text_Command.set('id', _id+ '_text' )
                text_Command.set('x', str(column_70+5))
                text_Command.set('y', str(current_height + (rightSide+1) * vSpacing-vGap))
                text_Command.text = out.scratchNames[0]
                text_Command.set('style', textStyle)

                
                line_Out = ET.SubElement(gg, "line")
                line_Out.set('x1', str(column_50) )
                line_Out.set('x2', str(column_80) )
                line_Out.set('y1', str(current_height + (rightSide+1) * vSpacing) )
                line_Out.set('y2', str(current_height + (rightSide+1) * vSpacing ))
                line_Out.set('style', inputLineStyleDefault )

                rightSide += 1
            
            for out in _adapter.output_values:
                _id = 'adapter_{an:s}_{on:s}'.format(an=_adapter.name, on=out.scratchNames[0])
                _id_text = idManager.getDisplayId_scratchOutputValue(out.scratchNames[0])
                
                text_Out = ET.SubElement(gg, "text")
                text_Out.set('x', str(column_50+5))
                text_Out.set('y', str(current_height + (rightSide+1) * vSpacing -vGap ))
                text_Out.text = out.name
                text_Out.set('style', textStyle)
                
                text_Command = ET.SubElement(gg, "text")
                text_Command.set('x', str(column_70+5 ))
                text_Command.set('y', str(current_height + (rightSide+1) * vSpacing - vGap))
                text_Command.text = out.scratchNames[0]
                text_Command.set('style', textStyle)
                
                line_Out = ET.SubElement(gg, "line")
                line_Out.set('x1', str(column_50) )
                line_Out.set('x2', str(column_80) )
                line_Out.set('y1', str(current_height + (rightSide+1) * vSpacing) )
                line_Out.set('y2', str(current_height + (rightSide+1) * vSpacing ))
                line_Out.set('style', inputLineStyleDefault )

                rect_Out = ET.SubElement(gg, "rect")
                rect_Out.set('id', _id + '_back')
                rect_Out.set('x', str(column_60))
                rect_Out.set('y', str(current_height + (rightSide+0) * vSpacing + vGap))
                rect_Out.set('width', str(column_70-column_60))
                rect_Out.set('height', str(vSpacing - vGap))
                rect_Out.set('style', rectStyle)

                # logger.debug("output_box id %s", _id)
                
                
                textValue_Out = ET.SubElement(gg, "text")
                textValue_Out.set('id', _id_text)
                textValue_Out.set('x', str(column_60+5))
                textValue_Out.set('y', str(current_height + (rightSide+1) * vSpacing -vGap))
                textValue_Out.text = '?'
                textValue_Out.set('style', textStyle)
                
                jScript += self.createOnclickOutputValue(_id+'_back', _id+'_back', _adapter.name, out.scratchNames[0])
                jScript += self.createOnclickOutputValue(_id_text   , _id+'_back', _adapter.name, out.scratchNames[0])
 
                rightSide += 1
            
            # keep track of current_height, add some gap between adapters.    
            current_height += h*vSpacing + vSpacing + 10
                     
        svg.set('width', str(column_90+1))
        svg.set('height', str(current_height+20))
        
        if sys.version_info.major == 2:
            svgText  = ET.tostring(svg)
            
        if sys.version_info.major == 3:
            svgText  = ET.tostring(svg).decode('utf-8')
        
        if debug:
            print(svgText)    
            logger.debug(svgText)

        #
        # javascript, tooltips
        #
        
        for _adapter in parentApplication.config.getAdapters():
            adapterId = 'adapter_{an:s}'.format(an=_adapter.name )
            

        jScript += '        let websocket = new WebSocket("ws://" + window.location.host + "/ws");  \n'
        jScript += """
    websocket.onmessage = function(e){
            let server_message = e.data;
            console.log(server_message);
            let jObj = JSON.parse(server_message); 
"""
        # --------------------------
        #
        # add the scratch command to id-mappers
        jScript +=         "        if ( jObj.command == 'scratch_input_command' ){ \n"
        res = idManager.getDisplayId_scratchInputCommandSummary()
        for sn in res.keys():
            jScript +=     "            if ( jObj.name == \"{name:s}\" ){{\n".format( name=sn )
            for ln in res[sn]:
                jScript += "                document.getElementById( \"{id:s}\" ).beginElement();\n".format(id=ln)
            jScript +=     "            }\n"   
        jScript +=         "        }\n"
        # --------------------------
           
        #
        # add the scratch command to id-mappers
        res = idManager.getDisplayId_scratchInputValueSummary()
        jScript +=         "         if ( jObj.command == 'scratch_input_value' ){ \n"
        for sn in res.keys():
            jScript +=     "             if ( jObj.name == \"{name:s}\" ){{\n".format( name=sn )
            for ln in res[sn]:
                jScript += "                 document.getElementById( \"{id:s}\" ).textContent = jObj.value;\n".format(id=ln)
            jScript +=     "             }\n"   
        jScript +=         "         }\n"
        # --------------------------
        #
        # add the scratch command to id-mappers
        res = idManager.getDisplayId_scratchOutputCommandSummary()
        jScript +=         "         if ( jObj.command == 'scratch_output_command' ){  \n"
        for sn in res.keys():
            jScript +=     "             if ( jObj.name == \"{name:s}\" ){{\n".format( name=sn )
            for ln in res[sn]:
                jScript += "                 document.getElementById( \"{id:s}\" ).beginElement();\n".format(id=ln)
            jScript +=     "             }\n"   
        jScript +=         "         } \n"

        #
        # add the scratch command to id-mappers
        jScript +=         "         if ( jObj.command == 'scratch_output_value' ){  \n"
        res = idManager.getDisplayId_scratchOutputValueSummary()
        for sn in res.keys():
            jScript +=     "             if ( jObj.name == \"{name:s}\" ){{\n".format( name=sn )
            for ln in res[sn]:
                jScript += "                 document.getElementById( \"{id:s}\" ).textContent = jObj.value;\n".format(id=ln)
            jScript +=     "             }\n"   
        jScript +=         "         }  \n"
        
            
        jScript += """        }
           
           websocket.onopen = function(){
               console.log('Connection open');
               document.getElementById("status.host").textContent ='Connection to scratchClient open';
               document.getElementById("status.host").style.background = 'green';
           }
           
           websocket.onclose = function(){
               console.log('Connection closed');
               document.getElementById("status.host").textContent ='Connection to scratchClient closed';
               document.getElementById("status.host").style.background = 'red';
           }
           
           // click on an object (send event)
           function click_Command (evt, id, command, scratch){
                try {
                    let message = JSON.stringify( { id:id, command:command, scratch:scratch } );
                    console.log( 'message: ' + message); 
                    websocket.send(message);
                }   catch(err) {
                    console.log( err.message );
                }
           }
        """
        #
        # Output Values, need an editor popup
        #
        html_preamble = """
            <!-- this is target structure -->
            
            <div id="DIV.float"        style="position:absolute;left:80px;top:80px;width:160px;height:60px;display:none;background-color:#f8f8f8;font-family:sans-serif;font-size:10;border-width=2px;border-color=x200000;border:3px coral solid;">
            
                <div id="HEADER.float" style="position:absolute;left:3px;top:3px;font-family:sans-serif;font-size:14;font-weight:bold;">header</div>
                <img id="qwInput" onclick="close_floatInput();" src="/icon/16x16_Delete.jpg" 
                                       style="position:absolute;right:3px;top:3px;background-color:#FFFFFF;"/>
                <input id='I00.float' size="24" 
                                       style="position:absolute;left:3px;bottom:3px;width:150px; font-family:sans-serif;font-size:12;fontWeight:normal;" />
            </div>
            
            <div id='status.host' style="position:fixed;width:240; left:0;bottom:0; background-color:#FFDDDD;font-family:sans-serif;font-size:12">
            </div>
            """
            
        if debug:
            #
            # place mouse coordinates to screen.    
            jScript += """
            function readMouseMove(e){
                var result_x = document.getElementById('x_result');
                var result_y = document.getElementById('y_result');
                result_x.innerHTML = e.clientX;
                result_y.innerHTML = e.clientY;
            }
            document.onmousemove = readMouseMove;
            """
            html_preamble += """   
                     <div id='x_result' style="position:fixed;width:100px; left:260px;bottom:0px; font-family:sans-serif;font-size:12" >X</div>
                     <div id='y_result' style="position:fixed;width:100px; left:360px;bottom:0px; font-family:sans-serif;font-size:12" >Y</div>
               
            """

        html_preamble += """
            <div style="position:absolute;width:280;right:0;top:0;background-color:#FFDDDD;font-family:sans-serif;font-size:12">
                 <ul id ='eventListId'  />
            </div>
        """
        
        jScript += """
                function close_floatInput(evt){
                    let tstObj = document.getElementById("DIV.float"); 
                    tstObj.style.display = 'none';
                }
                let pupup_state;
                function searchKeyPressInput_float(e){
                    
                    let textObj = document.getElementById("I00.float"); 
                    
                    console.log("command " + pupup_state.command);
                    console.log("name    " + pupup_state.name);
                    console.log("value   " + textObj.value);
                    
                    // look for window.event in case event isn't passed in
                    if (typeof e == 'undefined' && window.event) { e = window.event; }
                    if (e.keyCode == 13)
                    {
                        let message = JSON.stringify( { command: pupup_state.command, scratch:pupup_state.name, value:textObj.value } )
                        websocket.send ( message)  
                        textObj.value = ''
                    }
                } 
                function click_Value_input_float(evt, svgid, command, value_name){
                    console.log("command " + command);
                    console.log("name    " + value_name);
                    console.log("svgid   " + svgid);
                    
                    let svgText = document.getElementById(svgid);
                    let bbox = svgText.getBBox();
    
                    let divSvg = document.getElementById("DIV.svg");
                    
                    // var x = divSvg.offsetLeft + bbox.x;
                    // var y = divSvg.offsetHeight + bbox.y;

                    let x_svg = divSvg.getBoundingClientRect().left;
                    let y_svg = divSvg.getBoundingClientRect().top;

                    let tstHeader = document.getElementById("HEADER.float"); 
                    tstHeader.textContent = value_name;
                    
                    console.log("bbox.x " + bbox.x);
                    console.log("bbox.y " + bbox.y);
                    
                    console.log("divSvg.offsetLeft   " + divSvg.offsetLeft   );
                    console.log("divSvg.offsetHeight " + divSvg.offsetHeight );
                    console.log("divSvg.left         " + divSvg.left );
                    console.log("divSvg.top          " + divSvg.top  );

                    let tstObj = document.getElementById("DIV.float");
                     
                    console.log("set to x " +  (bbox.x + x_svg)      );
                    console.log("set to y " +  (bbox.y + y_svg)      );
                    
                    tstObj.style.left = (bbox.x + x_svg      ) + 'px';
                    tstObj.style.top  = (bbox.y + y_svg + 20 ) + 'px';
                    
                    tstObj.style.position = 'fixed'; //'absolute';
                    
                    tstObj.style.display = 'initial';
                    
                    pupup_state = { command: command, name: value_name};
                    
                    let textObj = document.getElementById("I00.float"); 
                    textObj.onkeypress = function(e){ searchKeyPressInput_float( e ); };
                    
                }
                """
                
        if debug: logger.debug (jScript)
        context = {'description'  : description,
                   'html_preamble': html_preamble, 
                   'svg'          : svgText ,
                   'jScript'      : jScript ,
                   'configName'   : xmlConfigName,
                   'debug_grid'   : debug_grid     }
        
        return self.render_response('template/adapters.html', context)
            
            


class AdapterAnimationWebSocket(tornado.websocket.WebSocketHandler):
    
    def __init__(self, args, kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, args, kwargs)
        self.terminated = None
        logger.info("AdapterAnimationWebSocket.init")

    def on_message(self, message):
        """
        Automatically sends back the provided ``message`` to
        its originating endpoint.
        """
        if debug: print("on_message: " + message)
        try:
            if sys.version_info.major < 3:
                if debug:
                    print('message.data:', message)
                md = message
                if debug:
                    print('md:', md)
                    
                msg = json.loads( md )
    
            if sys.version_info.major == 3:
                if debug:
                    print('message.data:', message)
                md = message
                if debug:
                    print('md:', md)
                msg = json.loads( md )
            
            if msg['command'] == 'input.command':
                publishSubscribe.Pub.publish('scratch.input.command.{name:s}'.format(name=msg['scratch']), { 'name':msg['scratch'] } ) 
                
            if msg['command'] == 'output.command':
                publishSubscribe.Pub.publish('scratch.output.command.{name:s}'.format(name=msg['scratch']), { 'name':msg['scratch'] } ) 
               
            if msg['command'] == 'input.value':
                publishSubscribe.Pub.publish('scratch.input.value.{name:s}'.format(name=msg['scratch']), { 'name':msg['scratch'], 'value':msg['value'] } ) 
                
            if msg['command'] == 'output.value':
                publishSubscribe.Pub.publish('scratch.output.value.{name:s}'.format(name=msg['scratch']), { 'name':msg['scratch'], 'value':msg['value'] } ) 
        
        except Exception as e:
            print("Exception !!", e)
            traceback.print_exc()
            
    def open(self):
        if debug: print("websocket open: " )

        self.terminated = False
        for _adapter in parentApplication.config.getAdapters():
            for inp in _adapter.inputs:
                for scratchName in inp.scratchNames:
                    publishSubscribe.Pub.subscribe("scratch.input.command.{name:s}".format(name=scratchName), self.inputCommand  )
            for inp in _adapter.input_values:
                for scratchName in inp.scratchNames:
                    publishSubscribe.Pub.subscribe("scratch.input.value.{name:s}".format(name=scratchName), self.inputValue )
            
            for out in _adapter.outputs:
                for scratchName in out.scratchNames:
                    publishSubscribe.Pub.subscribe("scratch.output.command.{name:s}".format(name=scratchName), self.outputCommand )
            for out in _adapter.output_values:
                for scratchName in out.scratchNames:
                    publishSubscribe.Pub.subscribe("scratch.output.value.{name:s}".format(name=scratchName), self.outputValue )
        
    def on_close(self, *args, **kwargs):
        if debug: print ("on_close", args, kwargs)
        self.terminated = True
        self.closed(22)
        
    def closed(self, code, reason=None):
        for _adapter in parentApplication.config.getAdapters():
            for inp in _adapter.inputs:
                for scratchName in inp.scratchNames:
                    publishSubscribe.Pub.unsubscribe("scratch.input.command.{name:s}".format(name=scratchName), self.inputCommand  )
            for inp in _adapter.input_values:
                for scratchName in inp.scratchNames:
                    publishSubscribe.Pub.unsubscribe("scratch.input.value.{name:s}".format(name=scratchName), self.inputValue )
            
            for out in _adapter.outputs:
                for scratchName in out.scratchNames:
                    publishSubscribe.Pub.unsubscribe("scratch.output.command.{name:s}".format(name=scratchName), self.outputCommand )
            for out in _adapter.output_values:
                for scratchName in out.scratchNames:
                    publishSubscribe.Pub.unsubscribe("scratch.output.value.{name:s}".format(name=scratchName), self.outputValue )        

    def _addMessage(self, message):
        """ called from the tornado.localIOloop.IOLoop.current().add_callback framework """ 
        if self.terminated == True:
            if debug: print("ScratchXWebSocketHandler[{cnt:d}] receive _addMessage while TERMINATED".format(cnt=self._instanceCount ))
        else:
            self.write_message (message, False )

        
    def inputValue(self, message):
        if debug: print("websocket inputValue", message)
        message['command'] = 'scratch_input_value'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, json.dumps(message) )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, json.dumps(message) )
        
    def inputCommand(self, message):
        if debug: print("websocket inputCommand", message)
        message['command'] = 'scratch_input_command'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, json.dumps(message) )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, json.dumps(message) )
                
    def outputValue(self, message):
        message['command'] = 'scratch_output_value'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, json.dumps(message) )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, json.dumps(message) )
            
    def outputCommand(self, message):
        message['command'] = 'scratch_output_command'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, json.dumps(message) )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, json.dumps(message) )
                

class ValueHandler_InputSide:
    def __init__(self):
        # eventHandler.register('ValueHandler', 'ValueHandler', self)
        pass
    
    def post(self, adapter, command, value):
        logger.debug("input  value called %s, %s, %s", adapter, command, value)
        # eventHandler.resolveValue(self, adapter, command, value, qualifier='input')
        return "no_return"

        return ""


class ValueHandler_OutputSide:
    def __init__(self):
        # eventHandler.register('ValueHandler', 'ValueHandler', self)
        pass
    

    def post(self, adapter, command, value):
        logger.debug("output value called %s, %s, %s", adapter, command, value)
        # eventHandler.resolveValue(self, adapter, command, value, qualifier='output')
        return ""

sendQueue = helper.abstractQueue.AbstractQueue() 

class ScratchXWebSocketHandler(tornado.websocket.WebSocketHandler):
    instanceCount = 0
    
    def __init__(self, args, kwargs):
        ScratchXWebSocketHandler.instanceCount += 1
        self._instanceCount =  ScratchXWebSocketHandler.instanceCount
        tornado.websocket.WebSocketHandler.__init__(self, args, kwargs)
        self.terminated = False

        scratchXHandler.subscribe(self)
        if debug: print("ScratchxWebSocketHandler[{cnt:d}].init".format(cnt=self._instanceCount) )
        
    def check_origin(self, origin):
        """Access-Control-Allow-Origin ..."""
        return True

    def open(self, *args, **kwargs):
        if debug: print("ScratchXWebSocketHandler[{cnt:d}], open".format(cnt=self._instanceCount) )
        scratchXHandler.event_connect()

    def on_close(self, *args, **kwargs):
        if debug: print ("ScratchXWebSocketHandler[{cnt:d}], on_close".format(cnt=self._instanceCount ))
        scratchXHandler.event_disconnect()
        scratchXHandler.unsubscribe(self)
        self.runMessageSend = False
        self.terminated = True
        
    def on_message(self, message):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug ( "ScratchXWebSocketHandler[{cnt:d}], received {m:s}".format(cnt=self._instanceCount, m=message ))
        try:
            if sys.version_info.major < 3:
                if debug:
                    print('message.data:', message)
                md = message
                if debug:
                    print('md:', md)
                    
                msg = json.loads( md )
    
            if sys.version_info.major >= 3:
                if debug:
                    print('message.data:', message)
                md = message
                if debug:
                    print('md:', md)
                msg = json.loads( md )
            
            if msg['command'] == 'input.command':
                publishSubscribe.Pub.publish('scratch.input.command.{name:s}'.format(name=msg['scratch']), { 'name':msg['scratch'] } ) 
                
            if msg['command'] == 'input.value':
                publishSubscribe.Pub.publish('scratch.input.value.{name:s}'.format(name=msg['scratch']), { 'name':msg['scratch'], 'value':msg['value'] } ) 
        
        except Exception as e:
            print("Exception !!", e, message)
            traceback.print_exc()

    
    def _addMessage(self, message):
        """ called from the tornado.localIOloop.IOLoop.current().add_callback framework """ 
        if self.terminated == True:
            if debug: print("ScratchXWebSocketHandler[{cnt:d}] receive _addMessage while TERMINATED".format(cnt=self._instanceCount ))
        else:
            self.write_message (message, False )
                   
    def inputValue(self, message):
        if debug: print("ScratchXWebSocketHandler[{cnt:d}] websocket inputValue {m:s}".format(cnt=self._instanceCount , m= message) )
        message['command'] = 'scratch_input_value'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, message )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, message )
        
    def inputCommand(self, message):
        if debug: print("ScratchXWebSocketHandler[{cnt:d}] websocket inputCommand {m:s}".format(cnt=self._instanceCount  , m= message) )
        message['command'] = 'scratch_input_command'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, message )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, message )
                 
    def sendValue(self, message):
        """established by configureCommandResolver"""
        if debug: print("ScratchXWebSocketHandler[{cnt:d}] websocket sendValue {m:s}".format(cnt=self._instanceCount  , m= str(message)) )
        message['command'] = 'scratch_output_value'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, message )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, message )
             
    def sendCommand(self, message):
        """established by configureCommandResolver"""
        if debug: print("ScratchXWebSocketHandler[{cnt:d}] websocket sendCommand {m:s}".format(cnt=self._instanceCount  , m= str(message)) )
        message['command'] = 'scratch_output_command'
        if useLocalIOloop:
            localIOloop.add_callback( self._addMessage, message )
        else:
            tornado.ioloop.IOLoop.current().add_callback( self._addMessage, message )

class JSName_VariableName:
    def __init__(self, variable, jsVariable):
        self.variable = variable
        self.jsVariable = jsVariable
    def __str__(self):
        return 'JSName_VariableName[variable=' + self.variable + ';' + 'jsVariable=' + self.jsVariable + ']'
        
class JSName_VariableName_Provider:
    """provide jsNames and variable names"""
    
    def __init__(self):
        self.variable_names = dict()
        
    def get(self, variable): 
           
        self.variable = variable
        if variable in self.variable_names:
            return self.variable_names[variable]
        else:
            jsVariable = "{s:s}".format( s=uuid.uuid3( uuid.NAMESPACE_URL ,variable).hex )
            j = JSName_VariableName( variable, jsVariable)
            self.variable_names[variable] = j
            
            return j
        
class ScratchXConfigHandler(BaseHandler):
    
    def initialize(self, extensionFile):
        self.extensionFile = extensionFile
        pass

    def set_default_headers(self):
        if debug: print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')
        
    def get(self):
        context = dict()
        context["scratchClient_host"] =  self.request.host
        variableName_Provider = JSName_VariableName_Provider()
        # the sensor names are used as variable names in javascript, so there are some limitations
        # on chars used in these names.
        
        # make a list of sensor_values
        sensor_names = []
        for _adapter in parentApplication.config.getAdapters():
            for out in _adapter.output_values:
                on= variableName_Provider.get( out.scratchNames[0] )
                sensor_names.append( on )
        context[ "sensor_names"] = sensor_names 
        
        send_events = []
        for _adapter in parentApplication.config.getAdapters():
            for out in _adapter.outputs:
                on= variableName_Provider.get( out.scratchNames[0] )
                send_events.append( on )
        context[ "send_events"] = send_events 
        
        #
        # multiple names per input are possible. therefor make a list of lists
        #  
        receive_events = []
        for _adapter in parentApplication.config.getAdapters():
            for out in _adapter.inputs:
                names = []
                for n in out.scratchNames:
                    names.append( variableName_Provider.get(n) )
                receive_events.append(names)
        context[ "receive_events"] = receive_events 
        
        #
        # multiple names per input are possible. therefor make a list of lists
        #  
        receive_values = []
        for _adapter in parentApplication.config.getAdapters():
            for out in _adapter.input_values:
                names = []
                for n in out.scratchNames:
                    names.append( variableName_Provider.get(n) )
                receive_values.append(names)
        context[ "receive_values"] = receive_values
        # unregister extension on connection loss 
        context ["reconnect"] = False
        
        if debug: print(context)
        self.render_response( self.extensionFile, context)
     
serverStarted = False
        
class ServerThread(threading.Thread):
    server = None
    remote = None
    config = None
    
    _stopEvent = None
    _running = None
    
    # to detect problems with multiple instances running
    usageCounter = 0
    
    def __init__(self, parent = None, config = None):
        if debug: print("ServerThread, init", serverStarted)
        threading.Thread.__init__(self, name="ServerThread_{usage:d}".format(usage = ServerThread.usageCounter) )
        
        ServerThread.usageCounter += 1
        
        self._stopEvent = threading.Event()
        self._running = threading.Event()
        
        _runThreads = True
        self.config = config
        global parentApplication
        parentApplication = parent
        
        # print("next: ServerThread, init finished")
        
        #
        # make dispatcher and config available on class level. This allows 'plugin' mechanism
        #
        self.listOfAdditionalPaths = []
        self.listOfAdditionalHandlers = []
        self.thread = None
        
    def websocketPlugin(self, name, route, pluginWebSocketClass):
        """enable insertion of webSocket-connection"""
        logger.debug("configure websocket plugin for " + name + ": " + str(pluginWebSocketClass) )
        self.listOfAdditionalHandlers.append(  { 'name':  name, 'route' : route, 'pluginWebSocketClass' : pluginWebSocketClass } )
        
    def htmlPlugin (self, name, htmlpath, comment=''):
        """enable insertion of html-connection""" 
        
        self.listOfAdditionalPaths.append(  { 'name':  name, 'htmlpath' : htmlpath, 'comment' : comment } )
       
    def start(self):
        """Start adapter Thread"""
        if debug: print("ServerThread, start", serverStarted)
        if serverStarted:
            print("ALERT " * 10)
            print("Server already started")
            return
        
        global _runThreads
        _runThreads = True

        self._stopEvent.clear()
        self._running.clear()
        
        self.thread = threading.Thread( name="ServerThread", target= self.run)
        self.thread.start()
        
        if debug: print("ServerThread, start completed")

    def stop(self):
        logger.debug("ServerThread, stop server")
        global _runThreads
        _runThreads = False
        self._stopEvent.set()
        
         
        if useLocalIOloop:
            global localIOloop
            iol = localIOloop
        else:
            iol = self.ioloop
        
        if iol != None:
            iol.stop()
            # directly access the ioloop from tornado.platform.asyncio.AsyncIOMainLoop
            # and threadsave issue stop
            # with this code, the thread is terminated. This works in tornado 5.1
            try:
                iol.asyncio_loop.call_soon_threadsafe( iol.asyncio_loop.stop )
            except Exception:
                pass
                    
        logger.debug("ServerThread, stop IOLoop stop")
        if self.server != None:
            self.server.stop()
        logger.debug("ServerThread, stop server join")
        
        if self.thread != None:
            self.thread.join( timeout=2.0)    
            if self.thread.isAlive():
                logger.warning("ServerThread, thread did not terminate")
                
        logger.debug("ServerThread, stop server completed")
        
    def stopped(self):
        return self._stopEvent.isSet()

    def make_app(self):
        
        settings = {
            'debug': False, 
            'autoreload' : False,
            # 'static_path': do not set. favicon.ico will be read from here, when set.
        }
    
        cPath = os.getcwd()
        if debug: print (cPath)
        
        handlers =  [
                        ## general pages
                        ( r"/"                          , ScratchClientMain,      {"additionalpaths" : self.listOfAdditionalPaths }     ),
                        
                        ## monitoring, simulation
                        ( r"/config"                    , ConfigHandler                 ),
                        ( r"/adapters"                  , AdaptersHandler               ),
                        ( r"/release"                   , ReleaseHandler                ),
                        
                        ( r"/usage14"                   , Usage14Handler                ),
                        
                        ( r"/ws"                        , AdapterAnimationWebSocket     ),
                        ( r"/command/input"             , CommandHandler_InputSide      ),
                        ( r"/command/output"            , CommandHandler_OutputSide     ),
                        ( r"/value/input"               , ValueHandler_InputSide        ),
                        ( r"/value/output"              , ValueHandler_OutputSide       ),
                        
                        ## scratchX connection
                        ## some convenience url provided
                        ##
                        (r"/scratchx/js/extension.js"   , ScratchXConfigHandler,  {"extensionFile": "scratchx/js/extension3.js"  }       ),
                        (r"/scratch2/js/extension.js"   , ScratchXConfigHandler,  {"extensionFile": "scratchx/js/extension3.js"  }       ),
                        
                        (r"/scratchx/js/extension2.js"  , ScratchXConfigHandler,  {"extensionFile": "scratchx/js/extension2.js" }        ),
                        (r"/scratch2/js/extension2.js"  , ScratchXConfigHandler,  {"extensionFile": "scratchx/js/extension2.js" }        ),
                        
                        (r"/scratchx/js/extension3.js"  , ScratchXConfigHandler,  {"extensionFile": "scratchx/js/extension3.js" }        ),
                        (r"/scratch2/js/extension3.js"  , ScratchXConfigHandler,  {"extensionFile": "scratchx/js/extension3.js" }        ),
                        
                        (r"/scratchx/ws"                , ScratchXWebSocketHandler      ),
                        
                        (r"/(scratchx/documentation/scratchClient\.html)"
                                                        , TemplateHandler      ,  {"path": "template"}    ),
                        (r"/(scratch2/documentation/scratchClient\.html)"
                                                        , TemplateHandler      ,  {"path": "template"}    ),
                        ## general purpose file connections 
                        (r"/(favicon.*)"            , tornado.web.StaticFileHandler, 
                                                                                  {"path": "htdocs/icon"} ),
                        (r"/(.*)"                       , tornado.web.StaticFileHandler, 
                                                                                  {"path": "htdocs"}      ),
                     ]

        for additionalHandler in self.listOfAdditionalHandlers:
            handlers.append( ( 
                               additionalHandler['route'], 
                               additionalHandler['pluginWebSocketClass']
                             ))

        return tornado.web.Application(handlers, **settings)
  

    def run(self):
        logger.debug("ServerThread thread started")
        #
        # see https://github.com/tornadoweb/tornado/issues/2308
        #
        try:
            # asyncio.set_event_loop_policy(tornado.platform.asyncio.AnyThreadEventLoopPolicy())
            asyncio.set_event_loop(asyncio.new_event_loop())
        except Exception as e:
            logger.warning("AnyThreadEventLoopPolicy exception " + str(e) )
            pass
        
        self.app = self.make_app()
        #
        # in case the 8080-port is already open and timeout running,
        # then reopen again and again till port is available
        if True:
            while not ( self.stopped()):
                try:
                    self.server = self.app.listen( 8080)
                    break
                except Exception as e:
                    time.sleep(0.3)
                    if debug:
                        traceback.print_exc()
                  
            if self.stopped():
                if debug: print("already stopped ??")
                return
        else:
            self.server = self.app.listen( 8080)
                    
        # tornado.log.enable_pretty_logging( )
        global localIOloop
        localIOloop = self.ioloop = tornado.ioloop.IOLoop.current()
        logger.debug("ServerThread tornado localIOloop start...")
        self.ioloop.start()
        logger.debug("ServerThread tornado localIOloop is terminated")
           
    def registerCommandResolver(self, _commandResolver):
        global commandResolver
        commandResolver = _commandResolver


class ScratchXHandler( scratchClient.ClientHandler ):
    
    def __init__(self, manager):  
        self.name="scratchXHandler"
        self.manager = manager 

        global scratchXHandler
        scratchXHandler = self
    
    def getName(self):
        return self.name
      
    def start(self):
        pass  
    
    def stop(self):
        pass  
    
    def event_disconnect(self):
        self.manager.setActive(self.getName(), False)
        
    def event_connect(self):
        self.manager.setActive(self.getName(), True)
