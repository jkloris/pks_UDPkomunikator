import socket
from socketHeader import *
from sender import *
from receiver import *

PORT = 8888
myIP = socket.gethostbyname(socket.gethostname())
dstIP = "192.168.1.11"
FORMAT = 'utf-8'
WINDOW_S = 2**11
WINDOW_R = 2**10
# BUFFSIZE  = 3200

FILENAME = "../blbosti/pic2.png"


if __name__ == "__main__":
    print("1...server\n2...client")
    x = int(input())

    # temp .. testovanie
    if x == 1:
        a = Receiver(PORT, WINDOW_R)
        a.start()

    elif x == 2:
        a = Sender(dstIP, PORT, WINDOW_S)
        a.start3WayHandshake(a.window)
        print("*Spojenie vytvorené*")

        fragments = chunkFile(FILENAME, a.window)

        for i,frag in enumerate(fragments):
            header = SocketHeader(len(frag), a.window, 1, frag)
            a.send(frag, header)
            # start timer
            msg, address = a.client.recvfrom(a.window)
            if not checkChecksum(msg):
                print("Chybny packet")

            print(f"Msg from {address}:  {len(msg)}")
        a.send(b'',SocketHeader(0, a.window, 8, b''))
