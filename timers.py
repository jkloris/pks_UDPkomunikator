import time
import threading
from socketHeader import *
import sys

class TimerTemp:
    def __init__(self, delay):
        self.delay = delay
        self.running = False
        self.thread = threading.Thread(target=self.loop)

    def start(self):
        self.thread.start()

    def action(self):
        pass

    def kill(self):
        self.running = False
        # self.thread.exit()


    def loop(self):
        self.running = True
        while self.running:
            time.sleep(self.delay)
            self.action()

# Casovac na refreshovanie spojenia (keep alive)
class TimerRefresh(TimerTemp):
    def __init__(self, sender):
        self.sender = sender
        self.delay = 5
        TimerTemp.__init__(self, self.delay)

    def action(self):
        h = SocketHeader(0, 16, 1, b'')
        self.sender.send(b'', h)

# Casovac, ktory odpocitava kolko casu este bude spojenie
class TimerAlive(TimerTemp):

    def __init__(self, sender):
        self.sender = sender
        self.delay = 1
        self.timeLeft = self.delay * 15
        TimerTemp.__init__(self, self.delay)

    def refreshTime(self):
        self.timeLeft = self.delay * 15
        # print("refreshed")

    def action(self):
        if self.timeLeft <= 0:
            self.running = False
            self.sender.CONNECTED = False
            print("disconnect")
            return
        self.timeLeft -= 1
        # print("*alive*")


class TimerMsg(TimerTemp):
    def __init__(self, sender, delay=0.01):
        self.sender = sender
        TimerTemp.__init__(self, delay)
        self.start()

    def action(self):
        print("TimerMsg action")
        if self.running:
            self.sender.sendMsgAgain(self.sender.lastMsg)
            print("TimerMsg sending...")
        self.kill()
