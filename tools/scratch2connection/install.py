#
# install a few files to connect scratch2 to 
import json
import os
import shutil
import traceback
import sys

help = """install script for scratchClient and scratch2 on raspberry pi.
Start this script as root:
sudo ~/scratchClient/tools/scratch2connection/install.py
"""
print(help)

scratch2_home = '/usr/lib/scratch2'
extension_json = scratch2_home + '/scratch_extensions/extensions.json'

extension_data = None

try:
    print("read file", extension_json)
    json_file = open(extension_json, 'r') 
    extension_data = json.load(json_file)
    json_file.close()
except Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    print("extension can't be installed; file does not exist.", extension_json)
    quit()

found = False
for entry in extension_data:
    if entry['name'] == 'ScratchClient':
        found = True

if found:
    print("extension is already installed")
    quit()
else:
    
    entry=dict()
    
    entry['name'] = 'ScratchClient'
    entry['type'] = 'extension'
    entry['file'] = 'scratchClient.js'
    entry['md5' ] = 'scratchClient.png'
    entry['url' ] = 'http://127.0.0.1:8080/scratch2/documentation/scratchClient.html'
    entry['tags'] = ['hardware', 'scratchClient']
    
    extension_data.append( entry )
    
try:
    print("modify file", extension_json)
    json_file = open(extension_json, 'w') 
    extension_data = json.dump(extension_data, json_file)
    json_file.close()
except Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    print("extension can't be installed; start script as root.", extension_json)
    quit()

try:
    
    shutil.copy2( 'scratchClient.png', scratch2_home + '/medialibrarythumbnails/' +  'scratchClient.png' )
    shutil.copy2( 'scratchClient.js' , scratch2_home + '/scratch_extensions/'     +  'scratchClient.js'  )
except  Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    print("files can't be copied; start script as root.", extension_json)
    quit()      