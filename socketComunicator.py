import socket
from socketHeader import *
from sender import *
from receiver import *
import time

_PORT = 8888
dstIP = "192.168.1.11"
FORMAT = 'utf-8'
FRAGSIZE = 2**10
BUFFSIZE  = 1500 # - bla bla

FILENAME = "../blbosti/pic2.png"

ROLE = None


def restart(x, PORT):

    if x == 1:
        ROLE = Receiver(PORT)
        ROLE.start()

    elif x == 2:
        ROLE = Sender(dstIP, PORT)
        ROLE.start3WayHandshake()
        print("*Spojenie vytvorené*")
        # ROLE.loop(FILENAME, BUFFSIZE)
        loopThread = threading.Thread(target=ROLE.loop)
        loopThread.start()

        while True:
            print("1: Poslat subor\n2: Koniec\n3: Prehod funkcie")
            cmd = int(input())

            if cmd == 1:
                fileThread = threading.Thread(target=ROLE.startSendingFile, args=(FILENAME, FRAGSIZE))
                fileThread.start()
                fileThread.join()
                continue
            elif cmd == 2:

                ROLE.timers["refresh"].running = False
                ROLE.timers["refresh"].thread.join()
                print("_________________________________________..dsdsadsaô")
                # TODO
                break
            elif cmd == 3:
                # NEFUNGUJE
                ROLE.switchClients()


if __name__ == "__main__":
    myIP = socket.gethostbyname(socket.gethostname())

    print("1...server\n2...client")
    x = int(input())

    # temp .. testovanie
    restart(x,_PORT)


def closeClientOpenServer(sender):
    port = sender.dstPORT
    print(threading.enumerate())
    sender.closeAllTimers()
    sender.CONNECTED = False
    sender.timers["refresh"].thread.join()
    sender.timers["alive"].thread.join()
    print(threading.enumerate())

    sender.client.close()
    print("___klient zavrety______")
    restart(1,port+1)
    # ROLE = Receiver(port)

def closeServerOpenClient(receiver):
    port = receiver.myPORT
    IP = dstIP
    receiver.RUNNING = False
    print(threading.enumerate())
    print("-----server zavrety------")
    time.sleep(5)
    restart(2,port+1)
    # ROLE = Sender(IP,port)
