import socket
from socketHeader import *
from sender import *
from receiver import *

PORT = 8888
myIP = socket.gethostbyname(socket.gethostname())
dstIP = "192.168.1.11"
FORMAT = 'utf-8'
FRAGSIZE = 2**10
BUFFSIZE  = 1500 # - bla bla

FILENAME = "../blbosti/pic.png"


if __name__ == "__main__":
    print("1...server\n2...client")
    x = int(input())

    # temp .. testovanie
    if x == 1:
        a = Receiver(PORT)
        a.start()

    elif x == 2:
        a = Sender(dstIP, PORT)
        a.loop(FILENAME, BUFFSIZE)




        while a.CONNECTED:
            pass