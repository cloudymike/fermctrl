#!/bin/bash
echo "Push boot buton  if loading does not start"
./loadmicropython.sh
sleep 20
./testmicropython.sh
if [ "$?" != "0" ]; then echo "ERROR Micropython not loaded"; exit 1; fi
./upip_install.sh
./testupip.sh
if [ "$?" != "0" ]; then echo "ERROR Pip packages not loaded"; exit 1; fi
echo "All packages loaded"
