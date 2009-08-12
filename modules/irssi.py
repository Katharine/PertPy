from PertBase import PertInterruptBase
import socket
import threading
import time

class IrssiServer(object):
    def __init__(self, host, port, password, name):
        self.host = host
        self.port = port
        self.password = password
        self.name = name

NETWORKS = (
    #IrssiServer('example.com', 6667, 'password', 'nickname'),
)

class PertIrssi(threading.Thread):
    irssi = None
    lcd = None
    interrupt = None
    nick = '__pertpy'
    def __init__(self, lcd, irssi, interrupt):
        super(PertIrssi, self).__init__()
        self.lcd = lcd
        self.irssi = irssi
        self.interrupt = interrupt
        self.setDaemon(True)
        self.start()
    
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.irssi.host, self.irssi.port))
        except socket.error, message:
            self.fail()
            return
        self.raw("USER pertpy 8 *: PertPy")
        self.raw("PASS %s" % self.irssi.password)
        self.raw("NICK %s" % self.nick)
        self.connected = True
        self.main_loop()
    
    def raw(self, message):
        self.socket.send(("%s\n" % message).encode('utf-8'))
    
    def main_loop(self):    
        while True:
            buff = ""
            while True:
                data = 0
                try:
                    data = self.socket.recv(512)
                except socket.error:
                    pass
                # Disconnected
                if data == 0 or not self.connected:
                    self.disconnected()
                    return
                data = (buff + data).split("\n")
                buff = data.pop()
                for line in data:
                    line = line.strip()
                    try:
                        line = line.decode('utf-8')
                    except UnicodeDecodeError, e:
                        pass
                    self.handle(line)
        
    def handle(self, line):
        origin = None
        if line[0] == ':':
            hostmask, line = line[1:].split(' ', 1)
            parts = hostmask.split('!', 1)
            nick = parts[0]
        
        parts = line.split(' :', 1)
        args = parts[0].split(' ')
        if len(parts) > 1:
            args.append(parts[1])
        
        command = args.pop(0).lower()
        
        if command == 'privmsg':
            if args[0] == self.nick:
                self.display(nick, nick, args[1])
            elif self.nick.lower() in args[1].lower():
                self.display(nick, args[0], args[1])
        elif command == 'nick':
            if nick == self.nick:
                self.nick = args[0]
    
    def display(self, origin, to, message):
        self.interrupt.interrupt()
        if message.startswith('\x01ACTION') and message[-1] == '\x01':
            self.lcd.display_string("%s: %s\n%s %s" % (self.irssi.name, to, origin, message[8:-1]))
        elif origin == to:
            self.lcd.display_string("%s: %s\n%s" % (self.irssi.name, to, message))
        else:
            self.lcd.display_string("%s: %s\n<%s> %s" % (self.irssi.name, to, origin, message))
        self.lcd.grab_attention()
        time.sleep(5)
        self.interrupt.release()
    
    def fail(self):
        self.interrupt.interrupt()
        self.lcd.display_string("IRC (%s):\nConnection failed." % self.irssi.name)
        self.lcd.grab_attention()
        time.sleep(5)
        self.interrupt.release()
    
    def disconnected(self):
        self.interrupt.interrupt()
        self.lcd.display_string("IRC (%s):\nDisconnected." % self.irssi.name)
        self.lcd.grab_attention()
        time.sleep(5)
        self.interrupt.release()

class PertInterrupt(PertInterruptBase):
    def run(self):
        for network in NETWORKS:
            PertIrssi(self.lcd, network, self)