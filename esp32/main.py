# Complete project details at https://RandomNerdTutorials.com

import textout
import time
import machine
import ntptime
import wlan
import tempreader
import awsiotconfig
from mqtt_reader_aws import MQTTReaderAWS


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
        self.tempDevice = tempreader.tempreader(self.unit)

        self.m = MQTTReaderAWS(
            awsiotconfig.MQTT_CLIENT_ID,
            awsiotconfig.MQTT_HOST,
            awsiotconfig.MQTT_PORT,
            awsiotconfig.MQTT_TOPIC,
            awsiotconfig.KEY_FILE,
            awsiotconfig.CERT_FILE)

        self.txt = textout.textout()

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
                temp = self.tempDevice.get_temp()
                time_str = "UTC: {4:02d}:{5:02d}:{6:02d}".format(*current_time)
                self.txt.clear()
                self.txt.centerline(time_str,3)

                self.txt.centerline("Temp: {:.1f}{}".format(temp,self.unit),4)

                self.txt.centerline("Target: {}".format(self.m.last_msg()),5)
                self.txt.show()


if __name__ == "__main__":
    m = mainloop()
    m.run()
