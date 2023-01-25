#!/bin/bash
HOSTNAME=$(grep hostname config.py | tr -d ' ' | cut -d "=" -f 2 | tr -d "\'" | tr -d "\"")
echo "MGTT server: $HOSTNAME"
mosquitto_sub -h "${HOSTNAME}" -t "tempctrlproj/lagercooler/settings"
