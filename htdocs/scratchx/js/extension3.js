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

(function(ext) {
    scratchClient_host = "${scratchClient_host}";
    
    scratchClient_status_number = 2;
    scratchClient_status_text = "Ready";

	
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

    
        ext.function_r = function(name) {
            if (name == 'undef')
                return 'undef';
            return data_cache[ name ];
        };
        
      
        ext.function_h = function( name ) {
            if (name == 'undef')
                return false; 
                
            ret = event_cache[ name ];
            event_cache[ name ] = false;
            return ret;
        };
	
    	// ----------------------- receive_events
        // events scratchx --> adapter

        ext.function_B_receive_events = function(name){
            if (name == 'undef')
                return;
                
            try {
                if ( ${js_debug} )
                    console.log('function function_receive_events ' + name);
 
                websocket.send( JSON.stringify( {  'command' : 'input.command',
                                                   'scratch' : name             } ) );
            }
            catch(err) {
                console.log( err.message );
            }
        };
	
        // ----------------------- receive_values
        // values scratchx --> adapter
        //
        ext.function_B_receive_values = function(name, value) {
            if (name == 'undef')
                return;
                
            try {
                if ( ${js_debug} )
                    console.log('function function_B_receive_values (' + name + ', ' + value + ')' );
                websocket.send( JSON.stringify( {  'command' : 'input.value',
                                                   'scratch' : name  ,
                                                   'value'   : value             } ) );
            }
            catch(err) {
                console.log( err.message );
            }
        };


        ext._getStatus = function() {
              return { status : scratchClient_status_number, 
                       msg    : scratchClient_status_text };
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
            ['r', 'variable %m.vs'            , 'function_r'                  , 'undef'       ],
            [' ', 'send name %m.vr value %s'  , 'function_B_receive_values'   , 'undef'       ],
            ['h', 'event %m.es'               , 'function_h'                  , 'undef'       ],
            [' ', 'broadcast %m.er'           , 'function_B_receive_events'   , 'undef'       ],
        ],
        
        menus: {
            vr: [ 'undef', 
                    // ${receive_values}
                    %  for names in receive_values:
                    %      for name in names:
                              '${name.variable}',
                    %      endfor    
                    %  endfor    
                    ],
                
            vs: [ 'undef', 
                    %  for name in sensor_names:
                         '${name.variable}',
                    % endfor    
                ],
    
            er: [ 'undef', 
                    %  for names in receive_events:
                    %      for name in names:
                              '${name.variable}',
                    %      endfor    
                    % endfor    
                ],
                
            es: [ 'undef', 
                    %  for name in send_events:
                         '${name.variable}',
                    % endfor    
                ],
        },
        url: 'http://${scratchClient_host}/scratchx/documentation/scratchClient.html'
  };

  ScratchExtensions.register('scratchClient', descriptor, ext);

})({});
