#!/bin/bash

# Will only load files newer than lastbuild
# lastbuild is touched at end
# To load all files, remove lastbuild

#set -x

loadfile () {
  if [[ $1 -nt ${CURDIR}/lastbuild ]]
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

usage ()
{
  echo "USAGE: $0 options"
  echo "-f     Fast load, do not load files not changed since last load"
  echo "-i     IP, implies used of webrepl"
  echo "-p     Password to use with webrepl, default: $WEBREPLPASS"
  echo "-P     Port to use for USB connection, default: $PORT"
  exit 0
}

IP=""
PORT='/dev/ttyUSB0'
WEBREPLPASS="MyPass"
FASTBUILD=0

CURDIR=$(pwd)
TOPDIR=${CURDIR%/*}
UPYEX=${TOPDIR}/micropythonexamples/DEVKITv1

while getopts "fi:hp:P:" arg; do
  case $arg in
    f)
      FASTBUILD=1
      ;;
    h)
      usage
      ;;
    i)
      IP=$OPTARG
      ;;
    p)
      WEBREPLPASS=$OPTARG
      ;;
    P)
      WEBREPLPASS=$OPTARG
      ;;
    *) usage
    ;;
  esac
done


if [ $FASTBUILD != 1 ]; then rm -f ${CURDIR}/lastbuild; fi

#Define some variables, change if needed
WLAN_CONFIG_PATH=~/secrets/wlanconfig.py


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
