#!/bin/bash
RESULT=$(timeout 5  ampy --port /dev/ttyUSB0 run chkmqtt.py)
RETURN=$?

if [ "$RETURN" != "0" ]; then echo "ERROR Non zero return code"; exit 1; fi
if grep -qv "__class__" <<< "$RESULT" ; then echo "ERROR Not getting mqtt"; exit 1; fi
echo "OK"

