/*
    Load a block from local scratchClient
    Accepts a url as a parameter which can include url parameters e.g. https://megjlow.github.io/extension2.js?name=SUN&ip=10.0.0.1
    
    Modified from https://megjlow.github.io/extensionloader.js
*/

new (function() {
    var ext = this;
    
    var descriptor = {
        blocks: [
            [' ', 'Load scratchClient blocks %m.type', 'loadBlock', 'verbose' ],
        ],
        menus: {
            type: [ 'workshop',
                    'verbose' ],
        },        
        url: 'http://www.warwick.ac.uk/tilesfortales'
    };
  
    ext._shutdown = function() {};
    
    ext._getStatus = function() {
        return {status: 2, msg: 'Device connected'}
    };
    
    ext.loadBlock = function(type) {
        if ( type == 'workshop' )
            ScratchExtensions.loadExternalJS("http://127.0.0.1:8080/scratchx/js/extension3.js");
        if ( type == 'verbose' )
            ScratchExtensions.loadExternalJS("http://127.0.0.1:8080/scratchx/js/extension2.js");
            
    };
    
    ScratchExtensions.register("extensionloader", descriptor, ext);
    
});