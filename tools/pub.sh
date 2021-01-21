#!/bin/bash

#Define some variables, change if needed

# These are your certificates, update with the path were you put it (and NOT in the repo)
CERT_FILE_PATH=../terraform/certs/tempctrl_cert.pem.crt
ROOT_CERT_FILE_PATH=../terraform/certs/AmazonRootCA1.pem
KEY_FILE_PATH=../terraform/certs/tempctrl_cert.private.key

WLAN_CONFIG_PATH=~/secrets/wlanconfig.py

# Server and topic
MQTT_HOST=$(cut -f 3 -d ' ' < ../terraform/endpoint.py)
MQTT_PORT=8883
MQTT_TOPIC="tempctrlpub"

mosquitto_pub \
  -h "${MQTT_HOST}" \
  --cert ${CERT_FILE_PATH} \
  --cafile ${ROOT_CERT_FILE_PATH} \
  --key ${KEY_FILE_PATH} \
  -t "${MQTT_TOPIC}" \
  -i "testmonitor" \
  -p ${MQTT_PORT} \
  -m "$1"
