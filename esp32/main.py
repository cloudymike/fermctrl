# Complete project details at https://RandomNerdTutorials.com

import time
import machine
import ntptime
import json
import wlan
import tempreader
import awsiotconfig
import relay
import mqttgcloud
import LED
import textout


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
        self.hysterisis=0.5
        self.temp=0.0
        self.target = 0.0
        self.tempDevice = tempreader.tempreader(self.unit)

        self.loadstate()

        self.m = mqttgcloud.MQTTgcloud()

    def storestate(self):
        state={}
        state['target'] = self.target
        with open('state.json', 'w') as outfile:
            json.dump(state, outfile)

    def loadstate(self):
        try:
            with open('state.json') as json_file:
                state = json.load(json_file)
            self.target = state['target']
        except:
            pass


    def thermostat(self):
        self.get_target()
        self.get_temp()
        if self.temp > self.target + self.hysterisis:
            relay.COLD.on()
            relay.HOT.off()
        elif self.temp < self.target - self.hysterisis :
            relay.HOT.on()
            relay.COLD.off()
        else:
            relay.COLD.off()
            relay.HOT.off()

    def get_target(self):
        targetstring = self.m.last_msg()
        try:
            self.target = float(targetstring)
        except:
            print("ERROR: No valid target")
        return(self.target)

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

                self.m.check_msg()
                self.thermostat()

                time_str = "UTC: {4:02d}:{5:02d}:{6:02d}".format(*current_time)
                self.txt.clear()
                self.txt.centerline(time_str,3)

                self.txt.centerline("Temp: {:.1f}{}".format(self.temp,self.unit),4)

                self.txt.centerline("Target: {}".format(self.target),5)
                self.txt.show()
            if min != old_min:
                old_min = min
                self.m.publish("{\"temperature\":" + str(self.temp) + "}")
                self.storestate()



if __name__ == "__main__":
    wlan.do_connect()
    LED.LED.value(1)
    m = mainloop()
    LED.LED.value(0)
    m.run()
