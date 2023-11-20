# All the tasks and corutines are called here
# Based on clean.py from mqtt client example 

# clean.py Test of asynchronous mqtt client with clean session.
# (C) Copyright Peter Hinch 2017-2019.
# Released under the MIT licence.

# Public brokers https://github.com/mqtt/mqtt.github.io/wiki/public_brokers

# The use of clean_session means that after a connection failure subscriptions
# must be renewed (MQTT spec 3.1.2.4). This is done by the connect handler.
# Note that publications issued during the outage will be missed. If this is
# an issue see unclean.py.

from mqtt_as import MQTTClient
from mqtt_as import config
import uasyncio as asyncio
import machine
import mainloop
import wlanconfig
import config as fermctrlconfig

print("Starting simple")

ml = mainloop.mainloop() 

# Subscription callback
def sub_cb(topic, msg, retained):
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    ml.setMessage(msg.decode())

async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe(fermctrlconfig.app_topic, 1)

async def main(client,ml):
    print('Starting async main')
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        return
    n = 0
    while True:
        await asyncio.sleep(5)
        # If WiFi is down the following will pause for the duration.
        await client.publish(bytes(fermctrlconfig.device_topic, 'utf-8'), ml.currentStatus(), qos = 1)
        print('At topic {} published {}'.format(fermctrlconfig.device_topic,ml.currentStatus()))
 
# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True
config['server'] = fermctrlconfig.hostname
config['ssid'] = wlanconfig.ESSID
config['wifi_pw'] = wlanconfig.PASSWORD




# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

asyncio.create_task(ml.run())

try:
    asyncio.run(main(client,ml))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop()


