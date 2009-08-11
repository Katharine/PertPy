#!/usr/bin/env python
# encoding: utf-8

from modules import mods
from pylcd.Manager import Manager as LCD
import time

def main():
    lcd = LCD()
    lcd.enable_backlight()
    lcd.display_string("PertPy Ready...")
    lcd.grab_attention(flashes=2, delay=0.2)
    time.sleep(3)
    while True:
        for mod in mods:
            print "Loading next module..."
            module = mod.PertModule(lcd)
            module.start()
            time.sleep(15)
            module.stop()
        print "Looping again."

if __name__ == '__main__':
    main()

