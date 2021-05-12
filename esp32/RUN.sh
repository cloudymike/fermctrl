#!/bin/bash

# Will only load files newer than lastbuild
# lastbuild is touched at end
# To load all files, remove lastbuild

#set -x

# Put your password for webrepl here, you would hate to type it forever
WEBREPLPASS=MyPass

loadfile () {
  if [[ $1 -nt lastbuild ]]
  then
    if [[ -d $1 ]]
    then
      for f in $(find $1 -name '*.py')
      do
        loadfile $f
      done
    elif [[ ! -f $1 ]]
    then
       echo "Missing file: $1"
       exit 1
    else

      if [ "$IP" == "" ]
      then
        ampy --port $PORT put $1
      else
        ../webrepl/webrepl_cli.py -p $WEBREPLPASS $1 $IP:/
      fi
    fi
  fi
}

IP=$1
PORT='/dev/ttyUSB0'

#Define some variables, change if needed
WLAN_CONFIG_PATH=~/secrets/wlanconfig.py

# Create command aliasPORT='/dev/ttyUSB0'
CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}
UPYEX=${TOPDIR}/micropythonexamples/DEVKITv1

echo "Loading certs, keys and configs"
loadfile ${WLAN_CONFIG_PATH}
loadfile ${TOPDIR}/gcloudconfig/config.py

echo "Loading programs"
loadfile ${UPYEX}/wlan/wlan.py
loadfile ${UPYEX}/LED/LED.py
loadfile ${UPYEX}/gcloud-pub/mqttgcloud.py
loadfile ${UPYEX}/gcloud-pub/third_party
loadfile ${UPYEX}/oled/ssd1306.py
loadfile ${UPYEX}/oled/gfx.py
loadfile ${UPYEX}/textout/textout.py

loadfile relay.py
loadfile tempreader.py
loadfile main.py

touch lastbuild

if [ "$IP" == "" ]
then
  sudo timeout 2  ampy --port /dev/ttyUSB0 run reset.py
fi
