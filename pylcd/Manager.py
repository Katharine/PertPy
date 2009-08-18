# encoding: utf-8

from __future__ import with_statement
import LCD
import threading
import time
import re
import textwrap

class PeriodicUpdateManager(threading.Thread):
    line_lock = None
    scrolling_lines = []
    sleep = 0.1
    
    def __init__(self, lcd):
        self.line_lock = threading.RLock()
        super(PeriodicUpdateManager, self).__init__()
        self.lcd = lcd
        self.setDaemon(True)
        self.start()
    
    def update_line(self, line):
        with self.line_lock:
            current_line = [x for x in self.scrolling_lines if x.line == line.line]
            if len(current_line) > 0:
                if current_line[0].content == line.content:
                    return
            self.remove_line(line.line)
            self.lcd.set_line(line.line, line.prefix + line.content[:(20-len(line.prefix) - len(line.suffix))] + line.suffix)
            # Don't bother doing the whole scrolling thing if it fits anyway...
            if len(line.prefix + line.content + line.suffix) > 20:
                line.reset_scroll = time.time() + 0.5
                self.scrolling_lines.append(line)
    
    def remove_line(self, num):
        with self.line_lock:
            self.scrolling_lines = [x for x in self.scrolling_lines if x.line != num]
    
    def run(self):
        while True:
            with self.line_lock:
                for line in self.scrolling_lines:
                    if line.reset_scroll is not False:
                        if time.time() >= line.reset_scroll:
                            if line.offset > 0:
                                line.offset = 0
                                line.reset_scroll = time.time() + 0.5
                            else:
                                line.reset_scroll = False
                        else:
                            continue
                    else:
                        line.offset += 1
                    if len(line.content) - line.offset + len(line.prefix) + len(line.suffix) < 20:
                        line.reset_scroll = time.time() + 0.5
                        continue
                    line_display = line.content[line.offset:(20-len(line.prefix)-len(line.suffix)+line.offset)]
                    self.lcd.set_line(line.line, line.prefix + line_display + line.suffix)
            time.sleep(self.sleep)

class ScrollingLine(object):
    def __init__(self, line=1, content='', prefix='', suffix=''):
        self.line = line
        self.content = content
        self.prefix = prefix
        self.suffix = suffix
        self.offset = 0
        self.reset_scroll = False

class Manager(object):
    backlight_enabled = False
    
    def __init__(self, port=None):
        if port is None:
            self.lcd = LCD.LCD()
        else:
            self.lcd = LCD.LCD(port)
        self.updater = PeriodicUpdateManager(self.lcd)
    
    def grab_attention(self, flashes=3, delay=0.02):
        for i in range(flashes):
            self.lcd.set_backlight_enabled(not self.backlight_enabled)
            time.sleep(delay)
            self.lcd.set_backlight_enabled(self.backlight_enabled)
            time.sleep(delay)
    
    def clear_screen(self):
        for i in range(1, 5):
            self.updater.remove_line(i)
        self.lcd.clear_screen()
    
    def set_line(self, number, content, scrolling=False, prefix='', suffix=''):
        if not scrolling:
            self.updater.remove_line(number)
            self.lcd.set_line(number, prefix + content + suffix)
        else:
            self.updater.update_line(ScrollingLine(line=number, content=content, prefix=prefix, suffix=suffix))
    
    def enable_backlight(self):
        self.backlight_enabled = True
        self.lcd.set_backlight_enabled(True)
    
    def disable_backlight(self):
        self.backlight_enabled = False
        self.lcd.set_backlight_enabled(False)
    
    def add_character(self, num, shape):
        shape = textwrap.dedent(shape)
        lines = shape.split('\n')
        if lines[0] == '':
            lines.pop(0)
        if lines[-1] == '':
            lines.pop()
        lines = lines[:8]
        top = True
        while len(lines) < 8:
            if top:
                lines[0:0] = ['']
            else:
                lines.append('')
            top = not top
        ints = []
        for line in lines:
            line = line.replace('_', ' ')
            line = line.replace(' ', '0')
            line = re.sub('[^0]', '1', line)
            line += '0' * (5 - len(line))
            ints.append(int(line[0:5], 2))
        self.lcd.add_new_character(num, ints)
    
    def display_string(self, string, start_line=1, end_line=4):
        for i in range(start_line, end_line + 1):
            self.updater.remove_line(i)
        paras = string.split('\n')
        output_lines = []
        for para in paras:
            lines = textwrap.wrap(para, 20)
            output_lines.extend(lines)
        pointer = 0
        for line in range(start_line, end_line + 1):
            if len(output_lines) <= pointer:
                self.lcd.set_line(line, '')
            else:
                self.lcd.set_line(line, output_lines[pointer])
            pointer += 1
