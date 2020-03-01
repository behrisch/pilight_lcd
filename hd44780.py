#!/usr/bin/python

import RPi.GPIO as GPIO
import time

class HD44780:

    def __init__(self, pin_rs=16, pin_e=5, pins_db=(6, 13, 19, 26),
                 pulse=0.0005, delay=0.0005, width=20, height=4, warn=False):
        self._pin_rs = pin_rs
        self._pin_e = pin_e
        self._pins_db = pins_db
        self._pulse = pulse
        self._delay = delay
        self._width = width
        self._height = height
        self._memoffset = (0x80, 0xC0, 0x80 + width, 0xC0 + width)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(warn)
        for pin in (self._pin_e, self._pin_rs) + self._pins_db:
            GPIO.setup(pin, GPIO.OUT)
        self.clear()

    def clear(self):
        self.cmd(0x33)
        self.cmd(0x32)
        self.cmd(0x28)
        self.cmd(0x0C)
        self.cmd(0x06)
        self.cmd(0x01)

    def cmd(self, bits, char_mode=False):
        GPIO.output(self._pin_rs, char_mode)
        for offset in (4, 0):
            for pin in self._pins_db:
                GPIO.output(pin, GPIO.LOW)
            for i, pin in enumerate(self._pins_db):
                if bits & (1 << (i + offset)):
                    GPIO.output(pin, GPIO.HIGH)
            time.sleep(self._delay)
            GPIO.output(self._pin_e, GPIO.HIGH)
            time.sleep(self._pulse)
            GPIO.output(self._pin_e, GPIO.LOW)
            time.sleep(self._delay)

    def message(self, text, start=0):
        for idx, l in enumerate(str(text).splitlines()):
            self.cmd(self._memoffset[start + idx])
            for char in (l + self._width * " ")[:self._width]:
                self.cmd(ord(char), True)

if __name__ == '__main__':
    lcd = HD44780()
    lcd.message("I'm Raspberry Pi\n  Take a byte!\n and a second")
