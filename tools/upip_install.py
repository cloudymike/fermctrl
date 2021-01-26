# Example of how to use upip

# First setup network
#   see wlan module for wlanconfig file
# pip install with packages for micropython (prefix micropython-)
# Check on the package, there are probably limitations
# profit


import network
import wlanconfig

def do_connect(essid,password):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(essid, password)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

if __name__ == "__main__":
    do_connect(wlanconfig.ESSID,wlanconfig.PASSWORD)
    import upip
    upip.install('micropython-uuid')
    upip.install('micropython-umqtt.robust')
