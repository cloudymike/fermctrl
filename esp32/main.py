# Complete project details at https://RandomNerdTutorials.com

import time
import machine
import ntptime
import json
import wlan
import tempreader
import relay
import mqttgcloud
import LED
import textout
import savestate

VERSION=0.1

# enable watchdog with a timeout of 5min
# Keep a long timeout so you can reload software before timeout
wdt = machine.WDT(timeout=300000)

AVAILABLE_COMMANDS = ['stop','run','pause']
class mainloop:
    def __init__(self):
        self.rtc = machine.RTC()

        self.txt = textout.textout()
        self.txt.text('Starting....')

        try:
            ntptime.settime()
        except:
            pass
            #Use old time

        self.unit='F'
        self.temprange=0.5   # Range to hold the temperature in
        self.hysterisis=0.1 # On off difference, to avoid toggling
        self.temp=0.0
        self.tempDevice = tempreader.tempreader(self.unit)



        self.state = savestate.readState()
        try:
            self.target = self.state['target']
        except:
            self.target = 0.0
        try:
            self.cmd = self.state['cmd']
        except:
            self.cmd = 'stop'


        # Rebuild the state with current values
        # Creates a clean file for the future
        self.writeStateFile()


        self.m = mqttgcloud.MQTTgcloud()

    def writeStateFile(self):
        self.state = {}
        self.state['target'] = self.target
        self.state['cmd'] = self.cmd
        savestate.writeState(self.state)


    def thermostat(self):
        self.get_target()
        self.get_temp()
        if self.temp > self.target + self.hysterisis + self.temprange:
            relay.COLD.on()
            relay.HOT.off()
        elif self.temp < self.target - self.hysterisis - self.temprange:
            relay.HOT.on()
            relay.COLD.off()
        elif self.temp < self.target + self.temprange and self.temp > self.target - self.temprange:
            relay.COLD.off()
            relay.HOT.off()
        else:
            pass


    def get_target(self):
        targetstring = self.m.last_msg()
        try:
            self.target = float(targetstring)
            self.writeStateFile()
            self.set_command('run')
        except:
            self.set_command(targetstring)
        return(self.target)

    def set_command(self, cmd):
        if cmd in AVAILABLE_COMMANDS:
            self.cmd = cmd
            self.writeStateFile()


    def get_temp(self):
        self.temp = self.tempDevice.get_temp()
        return(self.temp)

    def run(self):
        old_second = 99
        old_min = 99
        while True:
            #date_str = "Date: {1:02d}/{2:02d}/{0:4d}".format(*self.rtc.datetime())
            current_time = self.rtc.datetime()
            year,*z,hour,min,second,us=current_time

            # Cycle over x time
            if second != old_second:
                old_second = second
                LED.LED.value(abs(LED.LED.value()-1))
                wdt.feed()

                self.m.check_msg()
                self.thermostat()

                time_str = "UTC: {4:02d}:{5:02d}:{6:02d}".format(*current_time)
                self.txt.clear()
                self.txt.centerline(time_str,3)

                self.txt.centerline("Temp: {:.1f}{}".format(self.temp,self.unit),4)
                if self.cmd == 'run':
                    self.txt.centerline("Target: {}".format(self.target),5)
                else:
                    self.txt.centerline("{}".format(self.cmd),5)
                self.txt.centerline("Version: {}".format(VERSION),6)
                self.txt.show()
            if min != old_min:
                old_min = min
                self.m.publish("{\"temperature\":" + str(self.temp) + "}")
                # Write state file once a minute just in case
                # We should be able to remove this.
                self.writeStateFile()




if __name__ == "__main__":
    wlan.do_connect()
    LED.LED.value(1)
    m = mainloop()
    LED.LED.value(0)
    m.run()
