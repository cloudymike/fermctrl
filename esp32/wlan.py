# Very simple example of how to setup network
# Best run interactively
# Enter SSID and PASSWORD here or load file once and then
# run the function with the right parameters

import network
import wlanconfig

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(wlanconfig.ESSID,wlanconfig.PASSWORD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
