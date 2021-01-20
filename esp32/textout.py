# Complete project details at https://RandomNerdTutorials.com

from machine import Pin, I2C
import ssd1306
from time import sleep
import os
from time import sleep_ms
import gfx


class textout:
    def __init__(self):
        # ESP32 Pin assignment
        i2c = I2C(-1, scl=Pin(15), sda=Pin(4))

        # ESP8266 Pin assignment
        #i2c = I2C(-1, scl=Pin(5), sda=Pin(24))

        # Reset OLED
        oledReset=Pin(16, Pin.OUT)
        oledReset.value(0)
        sleep_ms(500)
        oledReset.value(1)

        self.oled_width = 128
        self.oled_height = 64
        self.oled = ssd1306.SSD1306_I2C(self.oled_width, self.oled_height, i2c)
        self.oled.fill(0)
        self.oled.show()

    def clear(self):
        self.oled.fill(0)

    def show(self):
        self.oled.show()

    def centerline(self, txt, line=4):
        txt = str(txt)
        Xstart = 64-len(txt)*4
        self.oled.text(txt, Xstart, line*8)
