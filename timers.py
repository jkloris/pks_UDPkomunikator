import time
import threading
from socketHeader import *
import sys

# Template na casovac
# @param delay : cas (s) po ktorych spusti funkciu action
class TimerTemp:
    def __init__(self, delay):
        self.delay = delay
        self.running = False
        self.thread = threading.Thread(target=self.loop)

    def start(self):
        self.thread.start()

    # cinnosti, ktoru vykonava po uplynuti casu
    def action(self):
        pass

    # prerusenia casovaca
    def kill(self):
        self.running = False

    # slucka, ktora vola acion az, kym sa casovac nevypne
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
        self.paused = False
        TimerTemp.__init__(self, self.delay)

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    # posle refresh spravu
    def action(self):
        if self.paused:
            return
        h = SocketHeader(0, 16, self.sender.msgNum, b'')
        self.sender.msgNum+=1
        self.sender.send(b'', h)


# Casovac, ktory odpocitava kolko casu este bude spojenie
class TimerAlive(TimerTemp):

    def __init__(self, sender):
        self.sender = sender
        self.delay = 1
        self.timeLeft = self.delay * 15
        TimerTemp.__init__(self, self.delay)

    # obnovi cas zostavajuceho spojenia
    def refreshTime(self):
        self.timeLeft = self.delay * 15
        # print("refreshed")

    def pause(self):
        self.timeLeft = self.delay * 1000

    # vypne spojenie
    def action(self):
        if self.timeLeft <= 0:
            self.running = False
            # self.sender.CONNECTED = False
            print("[TimerAlive] *no time left*")
            self.sender.endConnection()
            return
        self.timeLeft -= 1
        # print("*alive*")

# casovac na znovuposielanie sprav
# @param sender : odosielatel
# @param flag : flag odosielanej spravy
# @param msg : sprava
# @param num : poradove cislo spravy
class TimerMsg(TimerTemp):
    def __init__(self, sender, flag, msg, num, delay=0.1):
        self.msg = msg
        self.num = int(num)
        self.sender = sender
        self.flag = int(flag)
        TimerTemp.__init__(self, delay)
        self.start()

    # posle spravu
    def action(self):
        # print("TimerMsg action")
        if self.running:
            self.sender.sendMsgAgain(self.msg, self.flag, self.num)
            print(f"[TimerMsg] sending msg (num:{self.num}, flag:{self.flag})")
        # self.kill()


