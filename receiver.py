import socket
import threading
import base64
import time
from socketHeader import *
HEADERSIZE = 19




class Receiver:
    def __init__(self, port, window):
        self.myIP = socket.gethostbyname(socket.gethostname())
        self.myPORT = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.myIP, self.myPORT))
        self.RUNNING = True
        self.window = window

    def start(self):
        print("Server is starting..")
        while self.RUNNING:
            print("+")
            msg, address = self.server.recvfrom(self.window)
            handleTest(msg, address)
            # thread = threading.Thread(target=handleTest, args=(connection, address))
            # thread.start()
        print("end")


fw = open("testOutput.png", "wb")



def translateHeader(header):
    size = header[:2]
    fragNum = header[2:18]
    flag = header[18:19]
    print(size,fragNum,flag)
    return size


def handleTest(msg, address):
    print(f"Msg from {address}:")
    # print(msg)
    print(len(msg))
    size = translateHeader(msg[:HEADERSIZE])

    if size == 0:
        fw.close()
        return
    fw.write(msg[HEADERSIZE:])

def handleComm(msg, address):
    pass

