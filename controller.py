#!/usr/bin/env python
# encoding: utf-8

from modules import mods
from pylcd.Manager import Manager as LCD
import time
from threading import Event
import atexit

def shutdown(lcd):
    lcd.lcd.lock.acquire()
    lcd.disable_backlight()
    lcd.display_string("")

def main():
    lcd = LCD()
    lcd.display_string("PertPy setup in progress...")
    lcd.enable_backlight()
    atexit.register(shutdown, lcd)
    wait = Event()
    wait.set()
    for mod in mods:
        if hasattr(mod, 'PertInterrupt'):
            interrupt = mod.PertInterrupt(lcd, wait)
            interrupt.start()
    
    lcd.display_string("PertPy Ready...")
    lcd.grab_attention(flashes=2, delay=0.2)
    time.sleep(2)
    while True:
        for mod in mods:
            if hasattr(mod, 'PertModule'):
                print "Loading next module..."
                module = mod.PertModule(lcd, wait)
                wait.wait()
                module.start()
                time.sleep(15)
                module.stop()
        print "Looping again."

if __name__ == '__main__':
    main()

