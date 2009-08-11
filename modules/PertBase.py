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
        self.wait.wait()
        self.lcd.display_string('')
        while self.running:
            self.wait.wait()
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
        self.interrupter.wait()
        self.interrupter.clear()
    
    def release(self):
        self.interrupter.set()