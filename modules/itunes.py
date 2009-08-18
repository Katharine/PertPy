from PertBase import PertInterruptBase, PertBase
try:
    import appscript # http://pypi.python.org/pypi/appscript/
except ImportError:
    enabled = False
else:
    enabled = True
import time

if enabled:
    
    def itunes_running():
        return 'iTunes' in [x.name() for x in appscript.app('System Events').processes()]
    
    def display_track(lcd, track):
        lcd.set_line(1, "Now playing:")
        lcd.set_line(2, track.name(), scrolling=True)
        lcd.set_line(3, track.album(), scrolling=True)
        lcd.set_line(4, track.artist(), scrolling=True)

    class PertModule(PertBase):
        def update(self):
            if itunes_running():
                try:
                    display_track(self.lcd, appscript.app('itunes').current_track())
                except appscript.CommandError:
                    self.lcd.display_string('Nothing is playing.')
            else:
                self.lcd.display_string('iTunes is not running.')


    class PertInterrupt(PertInterruptBase):
        current_track = None
        def run(self):
            while True:
                while not itunes_running():
                    time.sleep(10)
                itunes = appscript.app('itunes')
                while True:
                    try:
                        if not itunes_running():
                            break
                        current = itunes.current_track()
                        if self.current_track is None:
                            self.current_track = current.database_ID()
                        elif self.current_track != current.database_ID():
                            self.current_track = current.database_ID()
                            self.interrupt()
                            display_track(self.lcd, current)
                            self.lcd.grab_attention()
                            time.sleep(3)
                            self.release()
                    except appscript.CommandError:
                        pass
                    time.sleep(5)
                time.sleep(10)