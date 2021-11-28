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
            "alive" : None,
            "msg" : None
        }
        self.fragNum = None
        self.fragments = None
        self.lastMsg = None



    def closeAllTimers(self):
        self.timers["refresh"].kill()
        self.timers["alive"].kill()


    # posle spravu na server
    # @param data: sprava v b'' tvare
    # @param header: class socketHeader
    def send(self, data, header):
        msg = header.header + data

        try:
            self.client.sendto(msg, (self.dstIP, self.dstPORT))
        except:
            return False
        return True

    def startSendingFile(self, filename, fragsize):
        self.fragments = chunkFile(filename, fragsize)
        self.lastMsg = self.fragments[0]
        self.send(self.fragments[0], SocketHeader(len(self.fragments[0]), 1, 0, self.fragments[0]))
        self.timers["msg"] = TimerMsg( self)
        self.fragNum=0


    def loop(self):
        while self.CONNECTED:
            msg, address = self.client.recvfrom(BUFFSIZE)
            print(f"Msg from {address}:  {translateHeader(msg)}")
            self.handleMsg(msg, address)


    def handleMsg(self, msg, address):
        if not checkChecksum(msg):
            print("TODO Sending NACK")  # TODO

        if not self.CONNECTED:
            return

        headerParams = translateHeader(msg[:HEADERSIZE])
        if headerParams[1] == 17:
            self.timers["alive"].refreshTime()
            return

        if headerParams[1] == 33:
            self.send(b'', SocketHeader(0, 33,0, b''))
            print("---switch 33 odoslany-----")
            from socketComunicator import closeClientOpenServer
            closeClientOpenServer(self)
            return

        if headerParams[1] == 2:
            self.sendMsgAgain(self.lastMsg)
            return

        if headerParams[1] == 1 and self.fragments != None:
            self.timers["msg"].kill() # Stop timer

            self.fragNum+=1
            if len(self.fragments) == self.fragNum:
                self.fragments = None
                self.send(b'', SocketHeader(0, 1, self.fragNum, b''))
                return
            header = SocketHeader(len(self.fragments[self.fragNum]), 1, self.fragNum, self.fragments[self.fragNum])
            self.lastMsg = self.fragments[self.fragNum]
            if self.fragNum == 2 :
                self.send( createError(self.fragments[self.fragNum] + header.header),  header)
                self.timers["msg"] = TimerMsg( self)
                return
            self.send(self.fragments[self.fragNum], header)
            self.timers["msg"] = TimerMsg( self)


    def sendMsgAgain(self, msg):
        self.send(msg, SocketHeader(len(msg), 1, self.fragNum, msg))


    def start3WayHandshake(self):
        if not self.send(b'', SocketHeader(0, 4,0, b'')):
            print("TWH ret false ")
            return False
        # TODO timer
        try:
            msg, address = self.client.recvfrom(BUFFSIZE)
        except:
            # print("TWH ret false ")
            return False
        print("ret True")
        headerParams = translateHeader(msg[:HEADERSIZE])
        print(headerParams)

        self.send(b'', SocketHeader(0, 1,1, b''))
        self.CONNECTED = True

        self.timers["alive"] = TimerAlive(self)
        self.timers["refresh"] = TimerRefresh(self)
        self.timers["alive"].start()
        self.timers["refresh"].start()
        return True


    def switchClients(self):
        self.send(b'', SocketHeader(0, 32,0, b''))
        #Todo timer


    # def endConnection(self):
    #     self.send(b'', SocketHeader(0, 64, b''))
    #     #Todo timer



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







