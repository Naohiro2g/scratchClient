/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

//
// this release does not provide a 'function number'
//
scratchClient_host = "${scratchClient_host}";

scratchClient_status_number = 2;
scratchClient_status_text = "Ready";


(function(ext) {
	
	##
	## data arriving from websocket are stored in a hashtable
	## last value wins.
	## the hashtables used decouple reading speed from scratch from websocket speed.
	##
	
	let data_cache = {}
	% for name in sensor_names:
		data_cache['${name}'] = '';
	% endfor
	
	##
	## broadcast events are registered 'true' when arriving
	## when the hat has fired, the events are reset to false.
	##
	
	let event_cache = {}
    % for name in send_events:
        event_cache['${name}'] = false;
    % endfor    
	
	
    console.log("scratchClient_host ..." + scratchClient_host );
   
    let addr = "ws://" + scratchClient_host + "/scratchx/ws";
    if ( ${js_debug} )
        console.log(addr);
    
    let websocket = null;

    function start_connection(){
    
        websocket = new WebSocket( addr );
    
        websocket.onopen = function(){
            if ( ${js_debug} )
                console.log('Websocket connection open!');
           
            scratchClient_status_number = 2;
            scratchClient_status_text = "Ready";
        };
    
        websocket.onmessage = function(e){
            let server_message = e.data;
            
            if ( ${js_debug} )
                console.log("onmessage " + e.data);
            
            let obj = JSON.parse(server_message);
          
            if ( obj.command == 'scratch_output_value'){
                data_cache[ obj.name ] = obj.value;
            }
            if ( obj.command == 'scratch_output_command'){
                event_cache[ obj.name] = true;
            }
        };
        
       websocket.onclose = function(){
           if ( ${js_debug} )
                console.log('Websocket connection closed');
       
           scratchClient_status_number = 0;
           scratchClient_status_text = "Disconnected";
           
           ## reconnect now
           ## when reconnect is allowed, then let the timer loop do its job
           ## else just stop
           ##
           % if ( context.get("reconnect") ):
                console.log('reconnect: let check_connection do its job');
                check_connection();
           % else:
                console.log("reconnect: unregister('scratchClient')");
                ScratchExtensions.unregister ('scratchClient'); 
           % endif
        };
    }

    function check_connection(){
        if ( !websocket || websocket.readyState == 3){ 
           start_connection();
        }
    }

    start_connection();
    % if ( context.get("reconnect") ):
        setInterval(check_connection, 5000);
    % endif

    % for name in sensor_names:
        ext.function_r_${name.jsVariable} = function() {
            return data_cache['${name.variable}'];
        };
    % endfor    
    
    % for name in send_events:
        ext.function_h_${name.jsVariable} = function() {
            ret = event_cache[ '${name.variable}' ];
            event_cache[ '${name.variable}' ] = false;
            return ret;
        };
    % endfor    

	
	// ----------------------- receive_events
    // events scratchx --> adapter

    % for names in receive_events:
        % if len(names) == 1:
            ext.function_B_${names[0].jsVariable}_${receive_fnc} = function() {
                try {
                    if ( ${js_debug} )
                        console.log('function function_B_${names[0].jsVariable}_${receive_fnc}');
 
                    websocket.send( JSON.stringify( {  'command' : 'input.command',
                                                       'scratch' : '${names[0].variable}'    } ) );
                }
                catch(err) {
                    console.log( err.message );
                }
            };
        % else:
            ext.function_B_${names[0].jsVariable} = function(evt_name) {
                try {
                    if ( ${js_debug} )
                        console.log('function function_B_${names[0].jsVariable} (' + evt_name + ')' );
                    websocket.send( JSON.stringify( {  'command' : 'input.command',
                                                       'scratch' : evt_name          } ) );
                }
                catch(err) {
                    console.log( err.message );
                }
            };
        % endif
    
    % endfor
	
    // ----------------------- receive_values
    // values scratchx --> adapter
    //
    % for names in receive_values:
        % if len(names) == 1:
            ext.function_B_${names[0].jsVariable} = function(value) {
                try {
                    if ( ${js_debug} )
                        console.log('function function_B_${names[0].jsVariable} (' + value + ')' );
                    websocket.send( JSON.stringify( {  'command' : 'input.value',
                                                       'scratch' : '${names[0].variable}'  ,
                                                       'value'   : value             } ) );
                }
                catch(err) {
                    console.log( err.message );
                }
            };
        % else:
            ext.function_B_${names[0].jsVariable} = function(evt_name, value) {
                try {
                    if ( ${js_debug} )
                        console.log('function function_B_${names[0].jsVariable} (' + evt_name + ',' + value + ')' );
                    websocket.send( JSON.stringify( {  'command' : 'input.value',
                                                       'scratch' : evt_name       ,
                                                       'value'   : value             } ) );
                }
                catch(err) {
                    console.log( err.message );
                }
            };
        % endif
    % endfor


    ext._getStatus = function() {
          return { status : scratchClient_status_number, 
                   msg : scratchClient_status_text };
    };
    
    ext._shutdown = function() {
        console.log('_shutdown');
        try {
            websocket.onclose = function () {}; 
            websocket.close();
        } catch(err) {
            console.log( err.message );
        }
    };

    var descriptor = {
    blocks: [
        ## ------------------------------------------------
        % for name in sensor_names:
            ['r', '${name.variable}'      , 'function_r_${name.jsVariable}'],
        % endfor    

        ## ------------------------------------------------
        % for name in send_events:
            ['h', '${name.variable}'      , 'function_h_${name.jsVariable}'],
        % endfor  
          
        ## ------------------------------------------------
        ## single events: one entry broadcast 'name'
        ## multiple events: selection broadcast [names]
        ## 
        % for names in receive_events:
          % if len(names) == 1:
            [' ', 'broadcast ${names[0].variable} '      , 'function_B_${names[0].jsVariable}'],
          % else:
            [' ', 'broadcast %m.sel'   , 'function_B_${names[0].jsVariable}', '${names[0].variable}' ],
          % endif
        % endfor    
        ## ------------------------------------------------
        ## single values: one entry broadcast 'name'
        ## multiple values: selection broadcast [names]
        ## 
        % for names in receive_values:
          % if len(names) == 1:
            [' ', 'send ${names[0].variable}, value %s'      , 'function_B_${names[0].jsVariable}'],
          % else:
            [' ', 'send %m.val, value %s'   , 'function_B_${names[0].jsVariable}', '${names[0].variable}' ],
          % endif
        % endfor    

    ],
    menus: {
        % for names in receive_events:
          % if len(names) > 1:
              sel  : [ 
              % for name in names:
                        '${name.variable}',
              % endfor
                    ],
          % endif
        % endfor    


        % for names in receive_events:
          % if len(names) > 1:
              val  : [ 
              % for name in names:
                        '${name.variable}',
              % endfor
                    ],
          % endif
        % endfor    
    },
    url: 'http://${scratchClient_host}/scratchx/documentation/scratchClient.html'
  };

  ScratchExtensions.register('scratchClient', descriptor, ext);

})({});
