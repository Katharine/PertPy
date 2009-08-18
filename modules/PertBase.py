from __future__ import with_statement
import threading
import time

class PertBase(threading.Thread):
    running = True
    interval = 1
    wait = None
    
    def __init__(self, lcd, wait):
        super(PertBase, self).__init__()
        self.setDaemon(True)
        self.lcd = lcd
        self.wait = wait
    
    def stop(self):
        self.running = False
        del self.lcd
    
    def run(self):
        if not hasattr(self, 'update'):
            return
        with self.wait:
            self.lcd.display_string('')
        while self.running:
            with self.wait:
                try:
                    self.update()
                except AttributeError:
                    pass
            time.sleep(self.interval)

class PertInterruptBase(threading.Thread):
    def __init__(self, lcd, interrupter):
        super(PertInterruptBase, self).__init__()
        self.setDaemon(True)
        self.lcd = lcd
        self.interrupter = interrupter
    
    def interrupt(self):
        self.interrupter.acquire()
    
    def release(self):
        self.lcd.clear_screen()
        self.interrupter.release()