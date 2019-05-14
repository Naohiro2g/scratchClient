
# logger writing to the desktop event system.
#
# pip3 install notify2
# apt-get install libnotify-bin
#
# # start, when needed:
# /usr/lib/notification-daemon/notification-daemon
#
# # check system with
# notify-send 'notify-system' 'working'
#
# attach logger to logging json files.
#
import logging
try:
    import notify2
except Exception:
    pass

class NotificationHandler(logging.Handler):
    
    def __init__(self):
        logging.Handler.__init__(self)
        try:
            notify2.init('scratchClient')
        except Exception:
            pass
        
    def emit(self, record):
        log_entry = self.format(record)
        try:
            n = notify2.Notification("scratchClient",
                             log_entry,
                             "dialog-information"   # Icon name
                            )
            n.show()
        except Exception:
            pass

