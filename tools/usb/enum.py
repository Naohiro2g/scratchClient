try:
    import usb.core
except ImportError:
    exit("""
    This library requires the usb module
      Install with: 
           sudo pip  install pyusb
           sudo pip3 install pyusb
    """)
    
devices = usb.core.find(find_all = True  )
for p in devices:
    print( p)
    
print("complete")