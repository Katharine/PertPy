import threading
import time

class PertBase(threading.Thread):
    running = True
    interval = 1
    def __init__(self, lcd):
        super(PertBase, self).__init__()
        self.setDaemon(True)
        self.lcd = lcd
        self.lcd.display_string('')
    
    def stop(self):
        self.running = False
        del self.lcd
    
    def run(self):
        if not hasattr(self, 'update'):
            return
        while self.running:
            self.update()
            time.sleep(self.interval)
