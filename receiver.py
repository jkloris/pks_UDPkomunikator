import socket
import threading
import time
import os

from socketHeader import *

BUFFSIZE  = 1500
FORMAT = 'utf-8'

class Receiver:
    def __init__(self, port):
        self.myIP = socket.gethostbyname(socket.gethostname())
        self.myPORT = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.myIP, self.myPORT))
        self.RUNNING = True
        self.CONNECTED = False
        self.fw = None

        self.msgNumStart = None
        self.fileSize = 0
        self.lastFragN = None
        # self.storagePath = "C:\\Users\\Lenovo T470\\PycharmProjects\\learning\\PKS_Z2"


    def start(self):
        print(f"[SERVER] Server is starting on [{self.myIP} ; {self.myPORT}]")
        while self.RUNNING:
            # print("+")
            msg, address = self.server.recvfrom(BUFFSIZE)
            self.handleMsg(msg, address)

        print("[SERVER] End")
        self.server.close()

    def handleMsg(self, msg, address):
        headerParams = translateHeader(msg[:HEADERSIZE])
        print(f"[SERVER] Msg from {address}:  [Segment Size: {headerParams[0]}B, Flag: {headerParams[1]}, Segment num: {headerParams[2]}]")




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
            return

        if headerParams[1] == 64:
            self.send(b'', SocketHeader(0, 65, headerParams[2], b''), address)
            return

        if headerParams[1] == 65:
            from socketComunicator import disconnectServer
            disconnectServer(self)
            return

        # FIN
        if headerParams[1] == 4:
            self.send(b'', SocketHeader(0, 5, headerParams[2], b''), address)
            if self.fw == None or self.fw.closed:
                return
            self.fw.close()
            print("[SERVER]: *Subor bol prijaty*")
            print(f"    Absolutna adresa: {os.path.abspath(self.fw.name)}")
            print(f"    Velkost suboru: {self.fileSize}B")
            self.fw = None
            self.fileSize = 0

            return

        if headerParams[1] == 1:

            if not checkChecksum(msg):
                print(f"[ERROR] Chybny segment")
                self.send(b'', SocketHeader(0, 2, headerParams[2], b''), address)
                return
            print(f"[SERVER] Bezchybny segment")

            self.fileSize += headerParams[0] - HEADERSIZE

            if self.fw == None:
                self.msgNumStart = headerParams[2]
                print("[SERVER] Receiving file")
                self.lastFragN = headerParams[2]
                name = msg[HEADERSIZE:].decode(FORMAT)
                self.fw = open(name, "wb")
                self.send(b'', SocketHeader(0, 1, headerParams[2], b''), address)
                return
            print(f"    Cislo fragmentu: {headerParams[2] - self.msgNumStart}, Velkost fragmentu: {headerParams[0] - HEADERSIZE}B")


            if self.lastFragN != headerParams[2]:
                self.fw.write(msg[HEADERSIZE:])
                self.lastFragN = headerParams[2]

        self.send(b'', SocketHeader(0, 1,headerParams[2], b''), address)

    def send(self, data, header, address):
        msg = header.header + data
        # print(msg, len(msg))
        self.server.sendto(msg, address)





