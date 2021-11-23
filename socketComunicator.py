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

FILENAME = "../blbosti/pic2.png"


if __name__ == "__main__":
    print("1...server\n2...client")
    x = int(input())

    # temp .. testovanie
    if x == 1:
        a = Receiver(PORT)
        a.start()

    elif x == 2:
        a = Sender(dstIP, PORT)
        a.start3WayHandshake()
        print("*Spojenie vytvorené*")

        fragments = chunkFile(FILENAME, FRAGSIZE)

        for i,frag in enumerate(fragments):
            header = SocketHeader(len(frag), 1, frag)
            a.send(frag, header)
            # start timer
            msg, address = a.client.recvfrom(BUFFSIZE)
            if not checkChecksum(msg):
                print("Chybny packet")

            print(f"Msg from {address}:  {len(msg)}")
        a.send(b'',SocketHeader(0, 8, b''))
