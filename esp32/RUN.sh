#!/bin/bash
PORT='/dev/ttyUSB0'
PUSHCMD="ampy --port $PORT put "
CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}


# Enter your path to your WLAN configuration file here, see ../wlan/wlanconfig.py for example
$PUSHCMD ~/secrets/wlanconfig.py

$PUSHCMD wlan.py
$PUSHCMD ssd1306.py
$PUSHCMD textout.py
$PUSHCMD tempreader.py
$PUSHCMD main.py
sudo timeout 2  ampy --port /dev/ttyUSB0 run reset.py
