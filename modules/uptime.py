from PertBase import PertBase
import subprocess

class PertModule(PertBase):
    def update(self):
        uptime = subprocess.Popen(['uptime'], stdout=subprocess.PIPE).communicate()[0].strip().split(' ')
        if uptime[4] != 'days':
            time = uptime[3]
        else:
            time = '%s %s %s' % tuple(uptime[3:6])
        load = tuple(uptime[-3:])
        
        self.lcd.set_line(1, "Uptime: %s" % time.strip(', '))
        self.lcd.set_line(2, "Load: %s %s %s" % load)
