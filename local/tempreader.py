import machine
import json
import ubinascii
from ds18x20 import DS18X20
from onewire import OneWire
import time



class tempreader:

    def __init__(self, unit='C'):

        pin = machine.Pin(18)
        o = OneWire(pin)

        self.d = DS18X20(o)
        self.devicelist = self.d.scan()
        self.unit = unit
        self.C = 0



    # Assume there is just one sensor
    def get_temp(self):
        all=self.get_temp_list()
        hexi = ubinascii.hexlify(self.devicelist[0])
        return(all[hexi])

    # For a full list of sensors get all
    def get_temp_list(self):
        tempdict = {}
        self.d.convert_temp()
        time.sleep_ms(750)

        # Multiple temperature sensors are OK with onewire bus
        for device in self.devicelist:
            try:
                self.C = self.d.read_temp(device)
            except:
                pass
                # Better luck next time

            if self.unit == 'F':
                temp=(self.C * 9/5) + 32
            else:
                temp=self.C
            tempdict[ubinascii.hexlify(device)] = temp
        return(tempdict)
