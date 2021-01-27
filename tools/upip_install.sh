#!/bin/bash

#Define some variables, change if needed

WLAN_CONFIG_PATH=~/secrets/wlanconfig.py

# Create command aliasPORT='/dev/ttyUSB0'
PORT='/dev/ttyUSB0'
PUSHCMD="ampy --port $PORT put "
CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}

echo "Loading packages"
$PUSHCMD ${WLAN_CONFIG_PATH}
$PUSHCMD ../esp32/wlan.py
timeout 20  ampy --port /dev/ttyUSB0 run upip_install.py
