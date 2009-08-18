#!/usr/bin/env python
# encoding: utf-8

from __future__ import with_statement
import modules
from pylcd.Manager import Manager as LCD
import time
from threading import RLock
import atexit
import ConfigParser

def shutdown(lcd):
    lcd.lcd.lock.acquire()
    lcd.disable_backlight()
    lcd.display_string("")

def main():    
    config = ConfigParser.SafeConfigParser()
    config.read(['config/general.conf'])
    lcd = LCD(config.get('Global', 'DisplayPort'))
    lcd.display_string("PertPy setup in progress...")
    if config.getboolean('Global', 'Backlight'):
        lcd.enable_backlight()
    else:
        lcd.disable_backlight()
    atexit.register(shutdown, lcd)
    waitlock = RLock()
    mods = modules.get_modules(config)
    if not mods:
        lcd.display_string('No modules loaded.')
        time.sleep(5)
        return
    for module in mods:
        if hasattr(module, 'PertInterrupt'):
            interrupt = module.PertInterrupt(lcd, waitlock)
            interrupt.start()
    
    lcd.display_string("PertPy Ready...")
    lcd.grab_attention()
    time.sleep(1)
    sleep_time = config.getint('Global', 'DisplayTime')
    while True:
        for mod in mods:
            print mod
            if hasattr(mod, 'PertModule'):
                module = mod.PertModule(lcd, waitlock)
                with waitlock:
                    lcd.clear_screen()
                    module.start()
                time.sleep(sleep_time)
                module.stop()
        print "Looping again."

if __name__ == '__main__':
    main()

