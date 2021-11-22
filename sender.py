import socket
from socketHeader import *

# BUFFSIZE  = 1500
# WINDOW = 2**16
# PORT = 8888
# IP = "192.168.1.11"
FORMAT = 'utf-8'

class Sender:
    def __init__(self, ip, port, window):
        self.dstIP = ip
        self.dstPORT = port
        self.window = window
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((ip, port))
        self.CONNECTED = False

    # posle spravu na server
    # @param data: sprava v b'' tvare
    # @param header: class socketHeader
    def send(self, data, header):
        msg = header.header + data

        self.client.sendto(msg, (self.dstIP, self.dstPORT))

    def start3WayHandshake(self, window):
        self.send(b'', SocketHeader(0, window, 4, b''))
        # TODO timer
        msg, address = self.client.recvfrom(window)

        if not checkChecksum(msg):
            # TODO check
            print("Zly packet")

        headerParams = translateHeader(msg[:HEADERSIZE])
        print(headerParams)
        self.window = headerParams[1]

        self.send(b'', SocketHeader(0, self.window, 1, b''))
        self.CONNECTED = True



# Rozdeli subor do bit casti podla velkosti fragmentu
# @return colletion: list casti
def chunkFile(file, buffsize):
    buffsize -= HEADERSIZE
    with open(file, "rb") as f:
        collection = []
        while True:
            chunk = f.read(buffsize)
            if not chunk:
               return collection
            collection.append(chunk)

# Rozdeli string do casti podla velkosti fragmentu
# @return colletion: list casti
def chunkString(string, buffsize):
    collection = []
    buffsize -= HEADERSIZE
    for i in range(0, len(string), buffsize):
        collection.append(string[i:i+buffsize].encode(FORMAT))
    return collection







