import socket
from socketHeader import *

BUFFSIZE  = 32000
# WINDOW = 2**16
# PORT = 8888
# IP = "192.168.1.11"
FORMAT = 'utf-8'

class Sender:
    def __init__(self, ip, port):
        self.dstIP = ip
        self.dstPORT = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((ip, port))

    # posle spravu na server
    # @param data: sprava v b'' tvare
    # @param header: class socketHeader
    def send(self, data, header):
        msg = header.header + data
        print(msg, len(msg))

        self.client.sendto(msg, (self.dstIP, self.dstPORT))

# Rozdeli subor do bit casti podla velkosti fragmentu
# @return colletion: list casti
def chunkFile(file):
    with open(file, "rb") as f:
        collection = []
        while True:
            chunk = f.read(BUFFSIZE)
            if not chunk:
               return collection
            collection.append(chunk)

# Rozdeli string do casti podla velkosti fragmentu
# @return colletion: list casti
def chunkString(string):
    collection = []
    for i in range(0, len(string), BUFFSIZE):
        collection.append(string[i:i+BUFFSIZE].encode(FORMAT))
    return collection







