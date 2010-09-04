from PertBase import PertBase
import urllib2

class PertModule(PertBase):
    def update(self):
        f = urllib2.urlopen("http://mit.kathar.in/reuse/")
        contents = f.read().split("\n")
        f.close()
        self.lcd.set_line(1, "[REUSE]")
        for i in range(0, 3):
            if len(contents) <= i:
                break
            self.lcd.set_line(i + 2, contents[i], scrolling=True)
