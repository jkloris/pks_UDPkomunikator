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
            checkChecksum(msg)
            self.handleTest(msg, address)
            self.send(b'',SocketHeader(0, 1,2, b''), address)
            # thread = threading.Thread(target=handleTest, args=(connection, address))
            # thread.start()
        print("end")

    def handleTest(self, msg, address):
        # kontrola duplicity

        print(f"Msg from {address}:")
        print(len(msg))
        headerParams = translateHeader(msg[:HEADERSIZE])

        if headerParams[0] == 0:
            fw.close()
            return
        fw.write(msg[HEADERSIZE:])

    def send(self, data, header, address):
        msg = header.header + data
        # print(msg, len(msg))
        print(address)
        self.server.sendto(msg, address)

fw = open("testOutput.png", "wb")


def translateHeader(headerBits):
    size = headerBits[:2]
    fragNum = headerBits[2:18]
    flag = headerBits[18:19]
    return [size, fragNum, flag]

def handleComm(msg, address):
    pass

def checkChecksum(data):
    ch = data[15:19]
    x = data[:15] + data[19:]
    y = zlib.crc32(x)
    a = int.from_bytes(ch, "big")
    t = a^y
    # print(y,a,t, "checking#####")
    if t == 0:
        return True
    return False