#!/bin/bash

#Define some variables, change if needed

# These are your certificates, update with the path were you put it (and NOT in the repo)
CERT_FILE_PATH=../terraform/certs/tempctrl_cert.pem.crt
ROOT_CERT_FILE_PATH=../terraform/certs/AmazonRootCA1.pem
KEY_FILE_PATH=../terraform/certs/tempctrl_cert.private.key

WLAN_CONFIG_PATH=~/secrets/wlanconfig.py

# Server and topic
#MQTT_HOST="a2d09uxsvr5exq-ats.iot.us-west-2.amazonaws.com"
MQTT_HOST=$(cut -f 3 -d ' ' < ../terraform/endpoint.py)
MQTT_PORT=8883
MQTT_PUB_TOPIC="tempctrlpub"
MQTT_SUB_TOPIC="tempctrlsub"

# Filename for cert and key on the esp32 device
CERT_FILE=cert
KEY_FILE=key

# Create command aliasPORT='/dev/ttyUSB0'
PORT='/dev/ttyUSB0'
PUSHCMD="ampy --port $PORT put "
CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}

# Create configuration file
cat > awsiotconfig.py << EOF
CERT_FILE = "${CERT_FILE}"
KEY_FILE = "${KEY_FILE}"

#if you change the ClientId make sure update AWS policy
MQTT_CLIENT_ID = "esp32"

MQTT_PORT = "${MQTT_PORT}"

#if you change the topic make sure update AWS policy
MQTT_PUB_TOPIC = "${MQTT_PUB_TOPIC}"
MQTT_SUB_TOPIC = "${MQTT_SUB_TOPIC}"

#Change the following to match your environment
MQTT_HOST = "${MQTT_HOST}"
EOF

echo "Loading certs, keys and configs"
$PUSHCMD ${CERT_FILE_PATH} ${CERT_FILE}
$PUSHCMD ${KEY_FILE_PATH} ${KEY_FILE}
$PUSHCMD ${WLAN_CONFIG_PATH}
$PUSHCMD awsiotconfig.py

echo "Loading programs"
$PUSHCMD wlan.py
$PUSHCMD LED.py
$PUSHCMD relay.py
$PUSHCMD mqtt_aws.py
$PUSHCMD ssd1306.py
$PUSHCMD gfx.py
$PUSHCMD textout.py
$PUSHCMD tempreader.py
$PUSHCMD main.py
sudo timeout 2  ampy --port /dev/ttyUSB0 run reset.py
