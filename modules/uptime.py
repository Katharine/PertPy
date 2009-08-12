from PertBase import PertBase
import subprocess

class PertModule(PertBase):
    def update(self):
        uptime = subprocess.Popen(['uptime'], stdout=subprocess.PIPE).communicate()[0].strip().split(' ')
        if 'users,' in uptime:
            end = uptime.index('users,') - 1
        else:
            end = uptime.index('user,') - 1
        time = ' '.join(uptime[uptime.index('up')+1:end])
        load = tuple(uptime[-3:])
        
        self.lcd.set_line(1, "Up: %s" % time.strip(', '))
        self.lcd.set_line(2, "Load: %s %s %s" % load)
