# Complete project details at https://RandomNerdTutorials.com

import textout
import time
import machine
import ntptime
import wlan
import tempreader


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

        self.txt = textout.textout()

    def run(self):
        old_second = 99
        while True:
            #date_str = "Date: {1:02d}/{2:02d}/{0:4d}".format(*self.rtc.datetime())
            current_time = self.rtc.datetime()
            year,*z,hour,min,second,us=current_time

            # Cycle over x time
            if second != old_second:
                old_second = second
                temp = self.tempDevice.get_temp()
                time_str = "UTC: {4:02d}:{5:02d}:{6:02d}".format(*current_time)
                self.txt.clear()
                self.txt.centerline(time_str,4)

                self.txt.centerline("Temp: {:.1f}{}".format(temp,self.unit),5)
                self.txt.show()


if __name__ == "__main__":
    m = mainloop()
    m.run()
