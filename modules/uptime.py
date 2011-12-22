from PertBase import PertBase

import subprocess
import time as thetime

class PertModule(PertBase):
    def update(self):
        uptime = subprocess.Popen(['uptime'], stdout=subprocess.PIPE).communicate()[0].strip().split(' ')
        if 'users,' in uptime:
            end = uptime.index('users,') - 1
        else:
            end = uptime.index('user,') - 1
        time = ' '.join(uptime[uptime.index('up')+1:end])
        load = tuple([x.strip(',') for x in uptime[-3:]])
        
        self.lcd.set_line(1, "Up: %s" % time.strip(', '))
        self.lcd.set_line(2, "Load: %s %s %s" % load)
        self.lcd.set_line(4, thetime.strftime('%H:%M:%S      %d %b'))
