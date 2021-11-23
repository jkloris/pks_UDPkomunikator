import socket
from socketHeader import *
from timers import *
BUFFSIZE  = 1500
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
        self.CONNECTED = False
        self.timers = {
            "refresh" : None,
            "alive" : None
        }
        self.fragNum = None
        self.fragments = None

    # posle spravu na server
    # @param data: sprava v b'' tvare
    # @param header: class socketHeader
    def send(self, data, header):
        msg = header.header + data

        self.client.sendto(msg, (self.dstIP, self.dstPORT))

    def loop(self, FILENAME, FRAGSIZE):
        self.start3WayHandshake()
        print("*Spojenie vytvorené*")
        self.timers["alive"] = TimerAlive(self)
        self.timers["refresh"] = TimerRefresh(self)
        self.timers["alive"].start()
        self.timers["refresh"].start()

        self.fragments = chunkFile(FILENAME, FRAGSIZE)
        self.send(self.fragments[0], SocketHeader(len(self.fragments[0]), 1, self.fragments[0]))
        self.fragNum=0

        while self.CONNECTED:
            msg, address = self.client.recvfrom(BUFFSIZE)
            print(f"Msg from {address}:  {len(msg)}")
            self.handleMsg(msg, address)

    def handleMsg(self, msg, address):
        if not checkChecksum(msg):
            print("TODO Sending NACK")  # TODO

        if not self.CONNECTED:
            return

        headerParams = translateHeader(msg[:HEADERSIZE])
        if headerParams[1] == 17:
           self.timers["alive"].refreshTime()

        if headerParams[1] == 1 and self.fragments != None:
            self.fragNum+=1
            if len(self.fragments) == self.fragNum:
                self.fragments = None
                self.send(b'', SocketHeader(0, 8, b''))
                return
            header = SocketHeader(len(self.fragments[self.fragNum]), 1, self.fragments[self.fragNum])
            self.send(self.fragments[self.fragNum], header)

    # for i, frag in enumerate(fragments):
    #     header = SocketHeader(len(frag), 1, frag)
    #     a.send(frag, header)
    #     # start timer
    #     msg, address = a.client.recvfrom(BUFFSIZE)
    #     if not checkChecksum(msg):
    #         print("Chybny packet")
    #
    #     print(f"Msg from {address}:  {len(msg)}")
    # a.send(b'', SocketHeader(0, 8, b''))



    def start3WayHandshake(self):
        self.send(b'', SocketHeader(0, 4, b''))
        # TODO timer
        msg, address = self.client.recvfrom(BUFFSIZE)

        if not checkChecksum(msg):
            # TODO check
            print("Zly packet--")

        headerParams = translateHeader(msg[:HEADERSIZE])
        print(headerParams)

        self.send(b'', SocketHeader(0, 1, b''))
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







