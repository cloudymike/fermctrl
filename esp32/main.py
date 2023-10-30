# Complete project details at https://RandomNerdTutorials.com

import time
import machine
import ntptime
import json
import wlan
import tempreader
import internaltempreader
import relay
import mqtt_local
import LED
import textout
import bignumber
import savestate
import config
import esp32

VERSION=0.5

# enable watchdog with a timeout of 5min
# Keep a long timeout so you can reload software before timeout
wdt = machine.WDT(timeout=300000)

#===================== Bubble counter 
BubbleCount = 0
LastBubbleMs = 0

def bubble_interrupt(pin):
    global BubbleCount
    global LastBubbleMs
    global interrupt_pin
    interrupt_pin = pin

    BubbleCount = BubbleCount + 1
    #print("There is a bubble....oooooOOOOO ")
    
#   currentms = time.ticks_ms()
#   if time.ticks_diff(currentms, LastBubbleMs) > 100:
#       BubbleCount = BubbleCount + 1
#       print("There is a bubble....oooooOOOOO ")
#   LastBubbleMs = currentms

def get_bubblecount():
    global BubbleCount
    bubblecount = BubbleCount
    BubbleCount = 0
    return(bubblecount)


pir = machine.Pin(4, machine.Pin.IN)
pir.irq(trigger=machine.Pin.IRQ_RISING, handler=bubble_interrupt)
#===================== Bubble counter end

class mainloop:
    def __init__(self):
        self.rtc = machine.RTC()

        self.txt = textout.textout()
        self.txt.text('Starting....')

        try:
            ntptime.settime()
        except:
            pass
            #Use old timegcloud

        self.unit='F'
        self.temprange=0.1   # Range to hold the temperature in, +/-
        self.hysterisis=0.1 # On off difference, to avoid toggling
        self.temp=0.0
        self.bubblecount = 0
        self.dutyOff = 0
        self.dutyCold = 0
        self.dutyHot = 0
        self.countOff = 0
        self.countCold = 0
        self.countHot = 0

        self.tempDevice = tempreader.tempreader(self.unit)

        try:
            dummy=self.tempDevice.get_temp()
        except:
            self.tempDevice = internaltempreader.internaltempreader(self.unit)
        self.profile = {'0':0}
        self.lastmessage = ""



        self.state = savestate.readState()
        try:
            self.target = self.state['target']
        except:
            self.target = 0.0
        try:
            self.profile = self.state['profile']
        except:
            self.profile = {'0':0}
        try:
            self.start_epoch = self.state['start_epoch']
        except:
            self.start_epoch = time.time()

        # for debugging
        #self.start_epoch = time.time() + 3*86400

        # Rebuild the state with current values
        # Creates a clean file for the future
        self.writeStateFile()


        self.m = mqtt_local.MQTTlocal(config.device_name, config.hostname, 1883, config.device_topic, config.app_topic)

    # Create a proper dict and save as a json file
    def writeStateFile(self):
        self.state = {}
        self.state['target'] = self.target
        self.state['start_epoch'] = self.start_epoch
        self.state['profile'] = self.profile
        savestate.writeState(self.state)


    def thermostat(self):
        self.get_mqttdata()
        self.current_target()
        self.get_temp()
        if self.temp > self.target + self.hysterisis + self.temprange:
            relay.COLD.on()
            relay.HOT.off()
            self.countCold += 1
        elif self.temp < self.target - self.hysterisis - self.temprange:
            relay.HOT.on()
            relay.COLD.off()
            self.countHot += 1
        elif self.temp < self.target + self.temprange and self.temp > self.target - self.temprange:
            relay.COLD.off()
            relay.HOT.off()
            self.countOff += 1
        else:
            pass


    def current_target(self):
        day,hour,min,second = self.run_time()
        self.target = self.profile['0']

        sorted_keys = sorted(self.profile, key=int)
        for key_day in sorted_keys:
            if int(key_day) > day:
                break;
            self.target = float(self.profile[key_day])
        #print("Today {}, using  temp {} in profile {}".format(day,self.target,self.profile))


    def get_mqttdata(self):
        targetstring = self.m.last_msg()
        if targetstring != self.lastmessage:
            self.lastmessage=targetstring
        try:
            new_profile = json.loads(targetstring)
            print('Got new target:{}'.format(new_profile))
            print('Old target:{}'.format(self.profile))
            if new_profile != self.profile:
                self.profile = new_profile
                self.start_epoch = time.time()
                self.writeStateFile()
        except:
            pass
            #print("Recieved unrecognized mqttdata")

        return()


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

    def display_detail(self):
        day,hour,min,second = self.run_time()
        time_str = "Day {}".format(day)
        self.txt.clear()
        #self.txt.centerline(self.profile,1)
        self.txt.centerline(time_str,3)

        self.txt.centerline("Temp: {:.1f}{}".format(self.temp,self.unit),4)
        self.txt.centerline("Target: {}".format(self.target),5)
        self.txt.show()

    def display_simple(self):
        self.txt.clear()
        day,hour,min,second = self.run_time()
        #self.txt.centerline("Day:{}      Tgt:{}".format(day,self.target),1)
        self.txt.leftline("Day:{}".format(day),1)
        self.txt.rightline("Tgt:{}".format(self.target),1)
        bignumber.bigTemp(self.txt.display(), self.temp, self.unit)


    def run(self):

        old_second = 99
        old_min = 99
        while True:

            #self.display_detail()

            day,hour,min,second = self.run_time()

            # Cycle over x time
            if second != old_second:
                self.display_simple()
                old_second = second
                LED.LED.value(abs(LED.LED.value()-1))
                wdt.feed()

                self.m.check_msg()
                self.thermostat()

                publish_json = {}
                publish_json["temperature"] = self.temp
                publish_json["bubblecount"] = self.bubblecount
                publish_json["dutyCold"] = self.dutyCold
                publish_json["dutyHot"] = self.dutyHot
                publish_json["dutyOff"] = self.dutyOff
                publish_json["target"] = self.target
                publish_json["day"] = day
                publish_json["profile"] = self.profile
                print("Publishing: {}".format(publish_json))
                self.m.publish(publish_json)
                self.writeStateFile()
 
            if min != old_min:
                old_min = min
                self.bubblecount = get_bubblecount()
                self.dutyCold = self.countCold
                self.dutyHot = self.countHot
                self.dutyOff = self.countOff
                self.countCold = 0
                self.countHot = 0
                self.countOff = 0





if __name__ == "__main__":
    wlan.do_connect(config.device_name)
    print("Connected to WIFI")
    LED.LED.value(1)
    print("Starting mainloop")
    m = mainloop()
    LED.LED.value(0)
    m.run()
