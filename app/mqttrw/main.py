
import sys
import os
import config
import json
import time

from concurrent.futures import TimeoutError
import paho.mqtt.client as mqtt

import redis

REDIS_SERVER=os.getenv('REDIS_SERVER', 'localhost')
MQTT_SERVER=os.getenv('MQTT_SERVER', 'localhost')

datastore = redis.Redis(host=REDIS_SERVER, port=6379, decode_responses=True)

# Set default current device list
datastore.ltrim('DeviceList',-1,-2)
for device_name in config.device_list:
    datastore.lpush('DeviceList',device_name)
    print('adding device {}'.format(device_name))


################### mqtt section ###################
# Should be run in different loop / container
# Remove printstatement when finished. For now it is good debugging
def on_message(client, userdata, message):
    PROFILE = {}
    TEMPERATURE='? '
    TARGET='? '
    DAY='? '
    BUBBLECOUNT='? '
    HEAT='? '
    COOL='? '

    topic = message.topic
    try:
        data = json.loads(message.payload)
    except:
        data = {}
    #print("message received ", data)
    print("message topic=", topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    #print(type(data))
    print("Data dictionary {}".format(data))

    deviceName = topic.split('/')[1]
    print('Device Name: {}'.format(deviceName))

    TEMPERATURE=str(data.get('temperature','?'))
    datastore.set('{}:TEMPERATURE'.format(deviceName), TEMPERATURE)
    BUBBLECOUNT=str(data.get('bubblecount','?'))
    datastore.set('{}:BUBBLECOUNT'.format(deviceName), BUBBLECOUNT)
    HEAT=str(data.get('heat','?'))
    datastore.set('{}:HEAT'.format(deviceName), HEAT)
    COOL=str(data.get('cool','?'))
    datastore.set('{}:COOL'.format(deviceName), COOL)
    TARGET=str(data.get('target','?'))
    datastore.set('{}:TARGET'.format(deviceName), TARGET)
    DAY=str(data.get('day','?'))
    datastore.set('{}:DAY'.format(deviceName), DAY)
    PF=str(data.get('profile',str({})))
    PF_STR = PF.replace("\'", "\"")
    PROFILE = json.loads(PF_STR)
    datastore.delete('{}:PROFILE'.format(deviceName))
    datastore.hset('{}:PROFILE'.format(deviceName), mapping=PROFILE)
    print("Temperature:{}   BubbleCount:{}   Target:{}   Day:{}".format(TEMPERATURE,BUBBLECOUNT,TARGET,DAY))
    print(f"Profile {PROFILE}.")

def send_data(data,device_name):
    global client
    app_topic = "{}/{}/{}".format(config.project,device_name,config.app_data)
    client.publish(app_topic,data)

# Main section. Should probably be broken out as main but wait until mqtt removed
# Host 0.0.0.0 makes it available on the network, may not be a safe thing
#    change to 127.0.0.1 to be truly local



#broker_address=config.hostname
broker_address=MQTT_SERVER
print("creating new instance")
client = mqtt.Client("fermctrlwebserver") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker on {}".format(broker_address))
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop

deviceList = datastore.lrange('DeviceList',0,999)
for deviceName in deviceList:
    deviceTopic = "{}/{}/{}".format(config.project,deviceName,config.device_data)
    print("Subscribing to topic",deviceTopic)
    client.subscribe(deviceTopic)

# Reasonable defaults at startup
for deviceName in deviceList:
    # Set all profile to be not updated, read from devices
    datastore.set('{}:UpdateProfile'.format(deviceName), 'FALSE')

print('Staring loop')
while(1):
    deviceList = datastore.lrange('DeviceList',0,999)
    for deviceName in deviceList:
        #print('Checking to update {}'.format(deviceName))
        if datastore.get('{}:UpdateProfile'.format(deviceName)) == 'TRUE':
            datastore.set('{}:UpdateProfile'.format(deviceName), 'FALSE')
            PROFILEnew=datastore.hgetall('{}:PROFILEnew'.format(deviceName))

            # Do not send empty data, conroller will not like it
            if len(PROFILEnew) != 0:
                profileJSON = json.dumps(PROFILEnew)
                data = profileJSON.encode("utf-8")
                print("Sending: {}".format(data))
                send_data(data,deviceName)

    time.sleep(1)