#!/bin/bash

mosquitto_pub -h  "127.0.0.1" -m {\"temperature\":\"42\"} -t "tempctrlproj/ferm1topic" -d
