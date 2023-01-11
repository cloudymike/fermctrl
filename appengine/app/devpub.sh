#!/bin/bash

mosquitto_pub -h  "127.0.0.1" \
-m {\"temperature\":\"62\"\,\"target\":\"42\"\,\"day\":\"1\"} \
-t "tempctrlproj/lagercooler/esp32data" -d
