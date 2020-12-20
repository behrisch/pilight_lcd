#!/usr/bin/python
# inspired by https://github.com/lrvick/raspi-hd44780
# see also https://www.sparkfun.com/datasheets/LCD/HD44780.pdf,
# especially for the set of availlable characters (page 17)
# some more sources for wiring which may help to make the backlight switchable somewhen:
# https://www.raspberrypi-spy.co.uk/2012/08/16x2-lcd-module-control-with-backlight-switch
# http://lcdproc.sourceforge.net/docs/lcdproc-0-5-5-user.html#hd44780-howto
# https://srm.gr/hd44780-lcd-screen-raspberry-pi-2-and-3-libreelec
# https://tutorials-raspberrypi.de/raspberry-pi-lcd-display-16x2-hd44780/
# https://www.electronicshub.org/interfacing-16x2-lcd-with-raspberry-pi/
# ftp://ftp.osuosl.org/.2/nslu2/sources/cvs/lcdproc/lcdproc/docs/hd44780_howto.txt

import RPi.GPIO as GPIO
import time
import threading

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
        self._vscroll_delay = 1
        self._lines = []
        self._current_offset = 0
        self._paused = False
        self._replace = [(u"\xe4", u"\xe1"), (u"\xf6", u"\xef"), (u"\xfc", u"\xf5")]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(warn)
        for pin in (self._pin_e, self._pin_rs) + self._pins_db:
            GPIO.setup(pin, GPIO.OUT)
        self.clear()
        t = threading.Thread(target=self.update)
        t.daemon = True
        t.start()

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

    def update(self):
        while True:
            if not self._paused:
                for idx, l in enumerate(self._lines[self._current_offset:self._current_offset + self._height]):
                    self.cmd(self._memoffset[idx])
                    for char in (l + self._width * " ")[:self._width]:
                        self.cmd(ord(char), True)
            if len(self._lines) > self._height:
                self._current_offset += 1
                if self._current_offset + self._height > len(self._lines):
                    self._current_offset = 0
                    time.sleep(self._vscroll_delay)
            else:
                self._paused = True
            time.sleep(self._vscroll_delay)

    def message(self, text, start=0):
        self._paused = True
        self._lines += [""] * (start - len(self._lines))
        for old, new in self._replace:
            text = text.replace(old, new)
        new_lines = text.splitlines()
        self._lines[start:start + len(new_lines)] = new_lines
        while self._lines[-1] == "":
            del self._lines[-1]
        self._paused = False


if __name__ == '__main__':
    lcd = HD44780()
    lcd.message("I'm Raspberry Pi\n  Take a byte!\n and a second")
