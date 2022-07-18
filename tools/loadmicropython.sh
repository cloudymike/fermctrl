#!/bin/bash
#PACKAGE=esp32-idf3-20200902-v1.13.bin

# Last working
#PACKAGE=esp32-idf3-20190529-v1.11.bin

# Latest tested
PACKAGE=esp32-20220117-v1.18.bin

if [ ! -f $PACKAGE ]
then
	wget https://micropython.org/resources/firmware/$PACKAGE
fi
esptool/esptool.py --port /dev/ttyUSB0 erase_flash
esptool/esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ./$PACKAGE
