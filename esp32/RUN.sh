#!/bin/bash

#Define some variables, change if needed
WLAN_CONFIG_PATH=~/secrets/wlanconfig.py

# Create command aliasPORT='/dev/ttyUSB0'
PORT='/dev/ttyUSB0'
PUSHCMD="ampy --port $PORT put "
CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}
UPYEX=${TOPDIR}/micropythonexamples/DEVKITv1

echo "Loading certs, keys and configs"
$PUSHCMD ${WLAN_CONFIG_PATH}
$PUSHCMD ${TOPDIR}/gcloudconfig/config.py

echo "Loading programs"
$PUSHCMD ${UPYEX}/wlan/wlan.py
$PUSHCMD ${UPYEX}/LED/LED.py
$PUSHCMD ${UPYEX}/gcloud-pub/mqttgcloud.py
$PUSHCMD ${UPYEX}/gcloud-pub/third_party
$PUSHCMD ${UPYEX}/oled/ssd1306.py
$PUSHCMD ${UPYEX}/oled/gfx.py
$PUSHCMD ${UPYEX}/textout/textout.py

$PUSHCMD relay.py
$PUSHCMD tempreader.py
$PUSHCMD main.py

sudo timeout 2  ampy --port /dev/ttyUSB0 run reset.py
