#!/bin/bash

#Define some variables, change if needed

WLAN_CONFIG_PATH=~/secrets/wlanconfig.py

# Create command aliasPORT='/dev/ttyUSB0'
PORT='/dev/ttyUSB0'
PUSHCMD="ampy --port $PORT put "
CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}
UPYEX=${TOPDIR}/micropythonexamples/DEVKITv1

echo "Loading packages"
$PUSHCMD ${WLAN_CONFIG_PATH}
PUSHCMD ${UPYEX}/wlan/wlan.py
timeout 20  ampy --port /dev/ttyUSB0 run upip_install.py
