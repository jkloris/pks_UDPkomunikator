import socket
import threading
import base64
import time

from socketHeader import *

class Receiver:
    def __init__(self, port, window):
        self.myIP = socket.gethostbyname(socket.gethostname())
        self.myPORT = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.myIP, self.myPORT))
        self.RUNNING = True
        self.CONNECTED = False
        self.window = window

    def start(self):
        print("Server is starting..")
        while self.RUNNING:
            print("+")
            msg, address = self.server.recvfrom(self.window)
            checkChecksum(msg)
            self.handleMsg(msg, address)

            # thread = threading.Thread(target=handleTest, args=(connection, address))
            # thread.start()
        print("end")

    def handleMsg(self, msg, address):
        if not checkChecksum(msg):
            print("TODO Sending NACK")  # TODO

        headerParams = translateHeader(msg[:HEADERSIZE])
        print(headerParams)
        # spravovanie 3way handshake
        if not self.CONNECTED:
            if headerParams[2] == 4:
                if self.window > headerParams[1]:
                    self.window = headerParams[1]
                self.send(b'', SocketHeader(0, self.window, 5, b''), address)
                return
            elif headerParams[2] == 1:
                self.CONNECTED = True
                return


        # TODO kontrola duplicity

        print(f"Msg from {address}:")
        print(len(msg))
        if headerParams[0] == HEADERSIZE: #tmp
            print(headerParams)
            fw.close()
            return
        fw.write(msg[HEADERSIZE:])

        self.send(b'', SocketHeader(0, self.window, 1, b''), address)

    def send(self, data, header, address):
        msg = header.header + data
        # print(msg, len(msg))
        print(address)
        self.server.sendto(msg, address)

fw = open("testOutput.png", "wb")


