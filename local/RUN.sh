#!/bin/bash

#Define some variables, change if needed

WLAN_CONFIG_PATH=~/secrets/wlanconfig.py

# Server and topic


# Create command aliasPORT='/dev/ttyUSB0'
PORT='/dev/ttyUSB0'
PUSHCMD="ampy --port $PORT put "
CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}


echo "MQTT_HOST='$(hostname -I | awk '{print $1}')'" >mqtthost.py
echo "MQTT_CLIENT_ID='esp32'" >> mqtthost.py
echo "MQTT_PORT=1883" >> mqtthost.py
echo "MQTT_TOPIC='tempctrlpub'" >> mqtthost.py

$PUSHCMD mqtthost.py


echo "Loading programs"
$PUSHCMD wlan.py
$PUSHCMD LED.py
$PUSHCMD relay.py
$PUSHCMD mqtt_reader.py
$PUSHCMD ssd1306.py
$PUSHCMD gfx.py
$PUSHCMD textout.py
$PUSHCMD tempreader.py
$PUSHCMD main.py
sudo timeout 2  ampy --port /dev/ttyUSB0 run reset.py

echo "Publish message to turn LED on and off"
echo "Loops forever so ctrl-C when done"
# Give it a chance to boot
sleep 10
while [ 1 ];
do
  TARGET=$((65 + $RANDOM % 10))
  echo $TARGET
  mosquitto_pub -t tempctrlpub -q 0 -m $TARGET
  sleep 60
done
