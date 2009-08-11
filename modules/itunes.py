from PertBase import PertInterruptBase, PertBase
import appscript # http://pypi.python.org/pypi/appscript/
import time

def display_track(lcd, track):
    lcd.set_line(1, "Now playing:")
    lcd.set_line(2, track.name(), scrolling=True)
    lcd.set_line(3, track.album(), scrolling=True)
    lcd.set_line(4, track.artist(), scrolling=True)

class PertModule(PertBase):
    def update(self):
        display_track(self.lcd, appscript.app('itunes').current_track())


class PertInterrupt(PertInterruptBase):
    current_track = None
    def run(self):
        itunes = appscript.app('itunes')
        while True:
            current = itunes.current_track()
            if self.current_track is None:
                self.current_track = current.database_ID()
            elif self.current_track != current.database_ID():
                print "Current track changed!"
                self.current_track = current.database_ID()
                self.interrupt()
                display_track(self.lcd, current)
                self.lcd.grab_attention()
                time.sleep(15)
                self.release()
            time.sleep(5)