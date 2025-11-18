# Complete project details at https://RandomNerdTutorials.com

import time
import machine
import ntptime
import json
#import wlan
import tempreader
import internaltempreader
import relay
#import mqtt_local
import LED
import textout
import bignumber
import savestate
import config
import esp32
import uasyncio as asyncio

VERSION=0.7

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
    print("There is a bubble....oooooOOOOO ")

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
        self.hysterisis=0.2 # On off difference, to avoid toggling
        self.temp=0.0
        self.bubblecount = 0
        self.cool = 0
        self.heat = 0
        self.publish_json={}

        self.tempDevice = tempreader.tempreader(self.unit)

        try:
            dummy=self.tempDevice.get_temp()
        except:
            self.tempDevice = internaltempreader.internaltempreader(self.unit)
        self.profile = {'0':0}
        self.dryhop1 = 0
        self.lastmessage = ""
        self.message = ""



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
            self.dryhop1 = self.state['dryhop1']
        except:
            self.dryhop1 = 0
        try:
            self.start_epoch = self.state['start_epoch']
        except:
            self.start_epoch = time.time()

        # for debugging
        #self.start_epoch = time.time() + 3*86400

        # Rebuild the state with current values
        # Creates a clean file for the future
        self.writeStateFile()


        #self.m = mqtt_local.MQTTlocal(config.device_name, config.hostname, 1883, config.device_topic, config.app_topic)

    # Create a proper dict and save as a json file
    def writeStateFile(self):
        self.state = {}
        self.state['target'] = self.target
        self.state['start_epoch'] = self.start_epoch
        self.state['profile'] = self.profile
        self.state['dryhop1'] = self.dryhop1
        savestate.writeState(self.state)


    def thermostat(self):
        self.get_mqttdata()
        self.current_target()
        self.get_temp()
        if self.temp > self.target + self.hysterisis + self.temprange:
            relay.COLD.on()
            relay.HOT.off()
            self.heat = 0
            self.cool = 1
        elif self.temp < self.target - self.hysterisis - self.temprange:
            relay.HOT.on()
            relay.COLD.off()
            self.heat = 1
            self.cool = 0
        elif self.temp < self.target + self.temprange and self.temp > self.target - self.temprange:
            relay.COLD.off()
            relay.HOT.off()
            self.heat = 0
            self.cool = 0
        else:
            pass

    def setMessage(self,message):
        self.message = message
        print(message)

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
        targetstring = self.message
        print("Message:{}".format(self.message))
        if targetstring != self.lastmessage:
            self.lastmessage=targetstring
            try:
                full_profile = json.loads(targetstring)
                temperatures_profile = full_profile['temperatures']
                print('Got new target:{}'.format(full_profile))
                print('Old target:{}'.format(self.profile))
                update=False
                if full_profile['dryhop1'] != self.dryhop1:
                    update=True
                    self.dryhop1 = full_profile['dryhop1']
                if temperatures_profile != self.profile:
                    update = True
                    self.profile = temperatures_profile
                if update:
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

    def currentStatus(self):
        data = bytes(json.dumps(self.publish_json), 'utf-8')
        return(data)

    # Just check once a day for this
    # Need to not dryhop for day 0. Leave this out for testing.
    def dryhop1Action(self,day,hour,minute,second):
        if (hour == 0 and minute == 0):
            if second < 10 and day == int(self.dryhop1):
            #if second < 10 and day == int(self.dryhop1) and day > 0:
                relay.dryhop1.value(1)
            else:
                relay.dryhop1.value(0)

    async def run(self):

        old_second = 99
        old_minute = 99
        LEDvalue=0;
        while True:
            await asyncio.sleep_ms(1000)
            #self.display_detail()

            day,hour,minute,second = self.run_time()

            # Cycle over x time
            if second != old_second:
                old_second = second
                # Actions every interval of seconds for C3
                if not (second % 4):
                    self.display_simple()
                    LEDvalue=(LEDvalue+1)%2
                    LED.LED.value(LEDvalue)
                    wdt.feed()

                    self.thermostat()
                    self.dryhop1Action(day,hour,minute,second)

                    publish_json = {}
                    publish_json["temperature"] = self.temp
                    publish_json["bubblecount"] = self.bubblecount
                    publish_json["heat"] = self.heat
                    publish_json["cool"] = self.cool
                    publish_json["target"] = self.target
                    publish_json["day"] = day
                    publish_json["dryhop1"] = self.dryhop1
                    publish_json["profile"] = self.profile
                    #print("Publishing: {}".format(publish_json))
                    self.publish_json=publish_json
                    self.writeStateFile()
                    #print(day,hour,minute,second)
                    #print(LEDvalue)
 
            if minute != old_minute:
                old_minute = minute
                self.bubblecount = get_bubblecount()

