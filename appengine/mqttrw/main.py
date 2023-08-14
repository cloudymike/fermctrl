
import sys
import config
import json
import time

from concurrent.futures import TimeoutError
import paho.mqtt.client as mqtt

import redis



datastore = redis.Redis(host='redis', port=6379, decode_responses=True)
################### mqtt section ###################
# Should be run in different loop / container
# Remove printstatement when finished. For now it is good debugging
def on_message(client, userdata, message):
    PROFILE = {}
    TEMPERATURE='? '
    TARGET='? '
    DAY='? '

    topic = message.topic
    try:
        data = json.loads(message.payload)
    except:
        data = {}
    print("message received ", data)
    print("message topic=", topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    print(type(data))
    print("Data dictionary {}".format(data))
    TEMPERATURE=str(data.get('temperature','?'))
    datastore.set('TEMPERATURE', TEMPERATURE)
    TARGET=str(data.get('target','?'))
    datastore.set('TARGET', TARGET)
    DAY=str(data.get('day','?'))
    datastore.set('DAY', DAY)
    PF=str(data.get('profile',str({})))
    PF_STR = PF.replace("\'", "\"")
    PROFILE = json.loads(PF_STR)
    datastore.delete('PROFILE')
    datastore.hset('PROFILE', mapping=PROFILE)
    print("Temperature:{}   Target:{}   Day:{}".format(TEMPERATURE,TARGET,DAY))
    print(f"Profile {PROFILE}.")

def send_data(data):
    global client
    if config.use_google:
        project_id = config.google_cloud_config['project_id']
        cloud_region = config.google_cloud_config['cloud_region']
        registry_id = config.google_cloud_config['registry_id']
        device_id = config.google_cloud_config['device_id']
        client = iot_v1.DeviceManagerClient()
        device_path = client.device_path(project_id, cloud_region, registry_id, device_id)
        result = client.send_command_to_device(request={"name": device_path, "binary_data": data})
    else:
        client.publish(config.app_topic,data)

# Main section. Should probably be broken out as main but wait until mqtt removed
# Host 0.0.0.0 makes it available on the network, may not be a safe thing
#    change to 127.0.0.1 to be truly local
broker_address=config.hostname
print("creating new instance")
client = mqtt.Client("fermctrlwebserver") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker on {}".format(broker_address))
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic",config.device_topic)
client.subscribe(config.device_topic)

while(1):
    if datastore.get('UpdateProfile') == 'TRUE':
        print("Sending profile data")
        datastore.set('UpdateProfile', 'FALSE')
        PROFILEnew=datastore.hgetall('PROFILEnew')

        print("PROFILEnew:{}.".format(PROFILEnew))

        # Do not send empty data, conroller will not like it
        if len(PROFILEnew) != 0:
            profileJSON = json.dumps(PROFILEnew)
            data = profileJSON.encode("utf-8")
            print("Sending: {}".format(data))
            send_data(data)

    time.sleep(1)