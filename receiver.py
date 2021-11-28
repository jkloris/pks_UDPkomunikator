import socket
import threading
import time

from socketHeader import *

BUFFSIZE  = 1500

class Receiver:
    def __init__(self, port):
        self.myIP = socket.gethostbyname(socket.gethostname())
        self.myPORT = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.myIP, self.myPORT))
        self.RUNNING = True
        self.CONNECTED = False
        self.fw = None

        self.TMPCOUNTER = 1

    def start(self):
        print("Server is starting..")
        while self.RUNNING:
            print("+")
            msg, address = self.server.recvfrom(BUFFSIZE)
            self.handleMsg(msg, address)

        print("end")
        self.server.close()

    def handleMsg(self, msg, address):
        headerParams = translateHeader(msg[:HEADERSIZE])
        print(f"Msg from {address}: {headerParams}")

        if not checkChecksum(msg):
            print(f"Error - Sending NACK")
            self.send(b'', SocketHeader(0,2,headerParams[2], b''), address)
            return
             #TODO



        # spravovanie 3way handshake
        if not self.CONNECTED:
            if headerParams[1] == 4:
                self.send(b'', SocketHeader(0, 5,headerParams[2], b''), address)
                return
            elif headerParams[1] == 1:
                self.CONNECTED = True
                return

        # zachyti refresh signal
        if headerParams[1] == 16:
            self.send(b'', SocketHeader(0, 17, headerParams[2], b''), address)
            return

        if headerParams[1] == 32:

            self.send(b'', SocketHeader(0, 33,headerParams[2], b''), address)
            return

        if headerParams[1] == 33:
            from socketComunicator import closeServerOpenClient
            closeServerOpenClient(self)
            pass


        if headerParams[1] == 1:
            if self.fw == None:
                print(".....receiving file")
                self.fw = open(str(self.TMPCOUNTER)+"testOutput.png", "wb")

            if headerParams[0] == HEADERSIZE:  # tmp
                self.fw.close()
                self.fw = None
                self.TMPCOUNTER+=1
                return
            print(f"####{headerParams[2]}")
            self.fw.write(msg[HEADERSIZE:])

        self.send(b'', SocketHeader(0, 1,headerParams[2], b''), address)

    def send(self, data, header, address):
        msg = header.header + data
        # print(msg, len(msg))
        self.server.sendto(msg, address)





