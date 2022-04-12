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
import bignumber
import savestate

VERSION=0.3

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
        self.temp_direction = ' '


        self.state = savestate.readState()
        try:
            self.target = self.state['target']
        except:
            self.target = 0.0
        try:
            self.cmd = self.state['cmd']
        except:
            self.cmd = 'stop'
        try:
            self.start_epoch = self.state['start_epoch']
        except:
            self.start_epoch = time.time()

        # Rebuild the state with current values
        # Creates a clean file for the future
        self.writeStateFile()


        self.m = mqttgcloud.MQTTgcloud()

    # Create a proper dict and save as a json file
    def writeStateFile(self):
        self.state = {}
        self.state['target'] = self.target
        self.state['cmd'] = self.cmd
        self.state['start_epoch'] = self.start_epoch
        savestate.writeState(self.state)


    def thermostat(self):
        self.get_target()
        self.get_temp()
        if self.temp > self.target + self.hysterisis + self.temprange:
            relay.COLD.on()
            relay.HOT.off()
            self.temp_direction = 'v'
        elif self.temp < self.target - self.hysterisis - self.temprange:
            relay.HOT.on()
            relay.COLD.off()
            self.temp_direction = '^'
        elif self.temp < self.target + self.temprange and self.temp > self.target - self.temprange:
            relay.COLD.off()
            relay.HOT.off()
            self.temp_direction = ' '
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
            if cmd == 'run' and self.cmd != 'run':
                self.start_epoch = time.time()
            self.cmd = cmd
            self.writeStateFile()


    def get_temp(self):
        self.temp = self.tempDevice.get_temp()
        return(self.temp)

    def run_time(self):
        current_secs = time.time() - self.start_epoch
        year,month,day,hour,min,second,dummy1,dummy2 = time.localtime(current_secs)
        day = day - 1
        if month == 2:
            day = day + 31
        return((day,hour,min,second))

    def display_simple(self):
        self.txt.clear()
        day,hour,min,second = self.run_time()
        self.txt.leftline("Day:{}".format(day),1)
        self.txt.rightline("Tgt:{}".format(self.target),1)
        self.txt.centerline("{}".format(self.temp_direction),1)
        bignumber.bigTemp(self.txt.display(), self.temp, self.unit)

    def run(self):
        old_second = 99
        old_min = 99
        while True:

            #self.display_detail()
            self.display_simple()

            day,hour,min,second = self.run_time()

            # Cycle over x time
            if second != old_second:
                old_second = second
                LED.LED.value(abs(LED.LED.value()-1))
                wdt.feed()

                self.m.check_msg()
                self.thermostat()

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
