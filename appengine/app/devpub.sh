#!/bin/bash
HOSTNAME=$(grep hostname config.py | tr -d ' ' | cut -d "=" -f 2 | tr -d "\'" | tr -d "\"")
echo "MGTT server: $HOSTNAME"

mosquitto_pub -h  "${HOSTNAME}" \
-m {\"temperature\":\"62\"\,\"target\":\"42\"\,\"day\":\"1\"} \
-t "tempctrlproj/lagercooler/esp32data" -d
