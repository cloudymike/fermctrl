# Complete project details at https://RandomNerdTutorials.com

import textout
import time
import machine
import ntptime
import wlan
import tempreader
import awsiotconfig
from mqtt_reader_aws import MQTTReaderAWS
import relay


class mainloop:
    def __init__(self):
        wlan.do_connect()
        self.rtc = machine.RTC()

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

        self.m = MQTTReaderAWS(
            awsiotconfig.MQTT_CLIENT_ID,
            awsiotconfig.MQTT_HOST,
            awsiotconfig.MQTT_PORT,
            awsiotconfig.MQTT_TOPIC,
            awsiotconfig.KEY_FILE,
            awsiotconfig.CERT_FILE)

        self.txt = textout.textout()

    def thermostat(self):
        self.get_target()
        self.get_temp()
        print("Thermostat, temp:{} target:{}".format(self.temp, self.target))
        if self.temp + self.hysterisis > self.target:
            relay.COLD.on()
        if self.temp - self.hysterisis < self.target:
            relay.HOT.on()

    def get_target(self):
        targetstring = self.m.last_msg()
        print(targetstring)
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
        while True:
            # Check message, if none, keep going
            # If in separate loop, use wait_msg that holds until there is a message
            self.m.check_msg()
            #date_str = "Date: {1:02d}/{2:02d}/{0:4d}".format(*self.rtc.datetime())
            current_time = self.rtc.datetime()
            year,*z,hour,min,second,us=current_time

            # Cycle over x time
            if second != old_second:
                old_second = second
                self.thermostat()
                time_str = "UTC: {4:02d}:{5:02d}:{6:02d}".format(*current_time)
                self.txt.clear()
                self.txt.centerline(time_str,3)

                self.txt.centerline("Temp: {:.1f}{}".format(self.temp,self.unit),4)

                self.txt.centerline("Target: {}".format(self.target),5)
                self.txt.show()


if __name__ == "__main__":
    m = mainloop()
    m.run()
