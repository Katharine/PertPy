from __future__ import division
from PertBase import PertInterruptBase, PertBase
try:
    import appscript # http://pypi.python.org/pypi/appscript/
    from appscript import k
except ImportError:
    enabled = False
else:
    enabled = True
import time

if enabled:
    
    def itunes_running():
        return 'iTunes' in [x.name() for x in appscript.app('System Events').processes()]
    
    def display_track(lcd, track, progress=False, state=False):
        if progress is False:
            lcd.set_line(1, "Now playing:")
        else:
            # Time display
            lcd.add_character(3, """
            XXXXX
            
            
            
            
            
            
            XXXXX
            """)
            lcd.add_character(4, """
            ___XX
            ___XX
            __XXX
            _XXXX
            _XXXX
            __XXX
            ___XX
            ___XX
            """)
            lcd.add_character(5, """
            XX
            XX
            XXX
            XXXX
            XXXX
            XXX
            XX
            XX
            """)
            chars_available = 16
            proportion = progress / track.duration()
            full_chars = int(proportion * chars_available)
            pixels = "1" * int((proportion * chars_available - full_chars) * 5)
            partial_char = "11111\n" + (pixels + "\n") * 6 + "11111"
            lcd.add_character(2, partial_char)
            progress_bar = "\xFF" * full_chars
            chars = full_chars
            if pixels:
                progress_bar += "\x02"
                chars += 1
            progress_bar += "\x03" * (chars_available - chars)
            # Status display
            if state == k.playing:
                lcd.add_character(0, """
                X
                XX
                XXX
                XXXX
                XXX
                XX
                X
                _____
                """)
            else:
                lcd.add_character(0, """
                XX XX
                XX XX
                XX XX
                XX XX
                XX XX
                XX XX
                _____
                """)
            lcd.set_line(1, "\x00 \x04%s\x05" % progress_bar)
        lcd.set_line(2, track.name(), scrolling=True)
        lcd.set_line(3, track.album(), scrolling=True)
        lcd.set_line(4, track.artist(), scrolling=True)

    class PertModule(PertBase):
        def update(self):
            if itunes_running():
                itunes = appscript.app('itunes')
                try:
                    state = itunes.player_state()
                    if state in (k.playing, k.pausing, k.paused):
                        display_track(self.lcd, itunes.current_track(), progress=itunes.player_position(), state=state)
                    else:
                        self.lcd.display_string("iTunes is not currently playing.")
                except appscript.CommandError:
                    self.lcd.display_string('iTunes is not responding.')
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