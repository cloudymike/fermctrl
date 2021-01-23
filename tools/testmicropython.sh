#!/bin/bash
RESULT=$(timeout 5  ampy --port /dev/ttyUSB0 run 42.py)
RETURN=$?

if [ "$RETURN" != "0" ]; then echo "ERROR Non zero return code"; exit 1; fi
if grep -qv "42" <<< "$RESULT" ; then echo "ERROR Not getting the meaning of life"; exit 1; fi
echo "OK"

