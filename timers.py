import time
import threading
from socketHeader import *

class TimerTemp:
    def __init__(self, delay):
        self.delay = delay
        self.running = False
        self.thread = threading.Thread(target=self.loop)

    def start(self):
        self.thread.start()

    def action(self):
        pass

    def loop(self):
        self.running = True
        while self.running:
            time.sleep(self.delay)
            self.action()

# Casovac na refreshovanie spojenia (keep alive)
class TimerRefresh(TimerTemp):
    def __init__(self, sender):
        self.sender = sender
        self.delay = 10
        TimerTemp.__init__(self, self.delay)

    def action(self):
        h = SocketHeader(0, 16, b'')
        self.sender.send(b'', h)

# Casovac, ktory odpocitava kolko casu este bude spojenie
class TimerAlive(TimerTemp):

    def __init__(self, sender):
        self.sender = sender
        self.delay = 1
        self.timeLeft = self.delay * 11
        TimerTemp.__init__(self, self.delay)

    def refreshTime(self):
        self.timeLeft = self.delay * 11
        print("refreshed")

    def action(self):
        if self.timeLeft <= 0:
            self.running = False
            self.sender.CONNECTED = False
            print("disconnect")
            return
        self.timeLeft -= 1
        print("*alive*")


    # def loop(self):
    #     while self.timeLeft > 0:
    #         time.sleep(1000)
    #
    #     print("Close connection")
    #     self.thread.join()
    #     #TODO
