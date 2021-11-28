import socket
from socketHeader import *
from sender import *
from receiver import *
import time

_PORT = 8880
dstIP = "192.168.1.13"
FORMAT = 'utf-8'
FRAGSIZE = 2**10
BUFFSIZE  = 1500 # - bla bla

FILENAME = "pic2.png"
FILEPATH = "../blbosti/" + FILENAME
ROLE = None


def restart(x, PORT):

    if x == 1:
        ROLE = Receiver(PORT)
        ROLE.start()

    elif x == 2:
        ROLE = Sender(dstIP, PORT)
        print("SSSSSSSSSSSSSSS")
        while not ROLE.start3WayHandshake():
            time.sleep(0.5)
        print("*Spojenie vytvorené*")
        # ROLE.loop(FILENAME, BUFFSIZE)
        loopThread = threading.Thread(target=ROLE.loop)
        loopThread.start()

        while True:
            print("1: Poslat subor\n2: Koniec(nop)\n3: Prehod funkcie")
            cmd = int(input())

            if cmd == 1:
                fileThread = threading.Thread(target=ROLE.startSendingFile, args=(FILENAME, FILEPATH, FRAGSIZE))
                fileThread.start()
                fileThread.join()
                continue
            elif cmd == 2:
                # nefunguje
                ROLE.timers["refresh"].running = False
                ROLE.timers["refresh"].thread.join()
                print("_________________________________________..dsdsadsaô")
                # TODO
                break
            elif cmd == 3:
                ROLE.switchClients()


if __name__ == "__main__":
    myIP = socket.gethostbyname(socket.gethostname())

    print("1...server\n2...client")
    x = int(input())

    # temp .. testovanie
    restart(x,_PORT)


def closeClientOpenServer(sender):
    port = sender.dstPORT
    # print(threading.enumerate())
    sender.closeAllTimers()
    sender.CONNECTED = False
    sender.timers["refresh"].thread.join()
    sender.timers["alive"].thread.join()
    # print(threading.enumerate())

    sender.client.close()
    print("___klient zavrety______")
    restart(1,port+1)

def closeServerOpenClient(receiver):
    port = receiver.myPORT
    IP = dstIP
    receiver.RUNNING = False
    # print(threading.enumerate())
    print("-----server zavrety------")
    restart(2,port+1)
