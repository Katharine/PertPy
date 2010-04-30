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
            lcd.add_character(1, """
            11111
            11111
            11111
            11111
            11111
            11111
            11111
            11111
            """)
            lcd.add_character(3, """
            11111
            00000
            00000
            00000
            00000
            00000
            00000
            11111
            """)
            lcd.add_character(4, """
            00011
            00011
            00111
            01111
            01111
            00111
            00011
            00011
            """)
            lcd.add_character(5, """
            11000
            11000
            11100
            11110
            11110
            11100
            11000
            11000
            """)
            chars_available = 16
            proportion = progress / track.duration()
            full_chars = int(proportion * chars_available)
            pixels = "1" * int((proportion * chars_available - full_chars) * 5)
            partial_char = "11111\n" + (pixels + "\n") * 6 + "11111"
            lcd.add_character(2, partial_char)
            progress_bar = "\x01" * full_chars
            chars = full_chars
            if pixels:
                progress_bar += "\x02"
                chars += 1
            progress_bar += "\x03" * (chars_available - chars)
            # Status display
            if state == k.playing:
                lcd.add_character(0, """
                10000
                11000
                11100
                11110
                11100
                11000
                10000
                00000
                """)
            else:
                lcd.add_character(0, """
                11011
                11011
                11011
                11011
                11011
                11011
                00000
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