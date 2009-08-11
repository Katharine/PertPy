# encoding: utf-8

from __future__ import with_statement
import serial
import struct
import logging
import textwrap
import time
import threading

LINE_STARTS = {
    1: 0x0,
    2: 0x40,
    3: 0x14,
    4: 0x54,
}

class LCDError(Exception): pass

class LCD(object):    
    connection = None
    port_name = None
    lock = None
    
    def __init__(self, port='/dev/tty.usbserial-A2000dLe'): # OS X gives me weird names.
        self.port_name = port
        self.lock = threading.RLock()
        with self.lock:
            self.connection = serial.Serial(port)
            self.connection.open()
            self.prepare()
    
    def __del__(self):
        self.connection.close()
        
    def prepare(self):
        self.cmd_string((0x38, 0x06, 0x10, 0x0C, 0x01))
        logging.debug("Sent startup sequence.")
    
    def command(self, byte, wait=0.001):
        self.connection.write(struct.pack('B', byte))
        time.sleep(wait)
    
    def set_line(self, line, string):
        string = string[0:20]
        string += ' ' * (20 - len(string))
        strbytes = self.string_bytes(string)
        start = LINE_STARTS[line]
        with self.lock:
            self.cmd_string((0x80 | start,))
            for byte in strbytes:
                self.command(byte)
    
    def update_line(self, line, pos, text, length=None):
        start = LINE_STARTS[line] + pos
        text = text[0:20 - pos]
        if length is not None:
            text = text[0:length]
            text += ' ' * (length - len(text))
        with self.lock:
            self.cmd_string(0x80 | start)
            for byte in self.string_bytes(text):
                self.command(byte)
    
    def display_string(self, string):
        lines = textwrap.wrap(string, 20)[:4]
        with self.lock:
            self.cmd_string(0x01)
            for i in range(len(lines)):
                self.set_line(i + 1, lines[i])
        
    def string_bytes(self, string):
        return [ord(x) for x in string]
    
    def set_backlight_enabled(self, on):
        if not on:
            self.cmd_string(0x02)
        else:
            self.cmd_string(0x03)
    
    def add_new_character(self, num, lines):
        if num < 0 or num > 8:
            raise LCDError, "You may only define up to eight characters."
        offset = num * 8
        lines = list(lines[:8])
        lines.extend((0,) * (8 - len(lines)))
        with self.lock:
            self.cmd_string(0x40 | offset)
            for line in lines:
                self.command(line)
    
    def cmd_string(self, commands):
        if isinstance(commands, int):
            commands = (commands,)
        logging.debug("Sending command sequence %s" % ', '.join([hex(x) for x in commands]))
        with self.lock:
            for command in commands:
                self.command(0xFE, 0.0017)
                self.command(command, 0.0017 if command < 4 else 0.001)
