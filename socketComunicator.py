import socket
from socketHeader import *
from sender import *
from receiver import *

HEADER = 19
PORT = 8888
myIP = socket.gethostbyname(socket.gethostname())
dstIP = "192.168.1.11"
FORMAT = 'utf-8'
WINDOW = 2**16
BUFFSIZE  = 32000

FILENAME = "../blbosti/pic.png"


if __name__ == "__main__":
    print("1...server\n2...client")
    x = int(input())
    if x == 1:
        a = Receiver(PORT, WINDOW)
        a.start()
    elif x == 2:
        a = Sender(dstIP, PORT)
        fragments = chunkFile(FILENAME)
        for i,frag in enumerate(fragments):
            header = SocketHeader(len(frag),i,1)
            a.send(frag, header)
        a.send(b'',SocketHeader(0,i,2))
