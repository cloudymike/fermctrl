#!/bin/bash

echo "Settingspublished from appengine"
mosquitto_sub -t Settingspublished &

echo "Publish dummy temperature"
echo "Loops forever press any key when done"

old_tty=$(stty --save)
# Minimum required changes to terminal.  Add -echo to avoid output to screen.
stty -icanon min 0;


while true ; do
    if read -t 0; then # Input ready
        read -n 1 char
        echo -e "\nRead: ${char}\n"
        break
    else # No input
        dummyjson={"temperature":"66"}
        mosquitto_pub -t BlueLED -q 0 -m $dummyjson
        echo "Publish $dummyjson"
        sleep 1
    fi
done

stty $old_tty
pkill -9 mosquitto_sub

echo "Quitting but there may be more messages in the queue so LED may keep blinking"
