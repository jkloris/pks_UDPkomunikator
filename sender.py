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
            "msg" : None,
            "switch" : None
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

    def startSendingFile(self, filename, filepath, fragsize):
        self.fragments = chunkFile(filepath, fragsize)
        self.lastMsg = chunkString(filename, fragsize)[0] #TODO chunks

        self.send(self.lastMsg, SocketHeader(len(self.lastMsg), 1, 0, self.lastMsg))
        self.timers["msg"] = TimerMsg(self, 1, chunkString(filename, fragsize)[0])
        self.fragNum = 0


    def loop(self):
        while self.CONNECTED:
            msg, address = self.client.recvfrom(BUFFSIZE)

            self.handleMsg(msg, address)

    # spracovanie sprav
    # msg je sprava
    def handleMsg(self, msg, address):
        headerParams = translateHeader(msg[:HEADERSIZE])
        print(f"[Klient] Msg from {address}:  [Size: {headerParams[0]}, Flag: {headerParams[1]}, Frag. num: {headerParams[2]}]")

        if not checkChecksum(msg):
            print("TODO Sending NACK")  # TODO

        if not self.CONNECTED:
            return


        # REFRESH + ACK
        if headerParams[1] == 17:
            self.timers["alive"].refreshTime()
            return

        # SWITCH + ACK
        if headerParams[1] == 33:
            # TODO zisti preco je NONE a otestovat
            # self.timers["switch"].kill()
            self.send(b'', SocketHeader(0, 33, 0, b''))
            from socketComunicator import closeClientOpenServer
            closeClientOpenServer(self)
            return

        if headerParams[1] == 65:
            # todo start timer
            self.send(b'', SocketHeader(0, 65, 2, b''))
            from socketComunicator import disconnectClient
            disconnectClient(self)
            return

        # FIN + ACK
        if headerParams[1] == 5:
            if self.timers["msg"]:
                self.timers["msg"].kill()
            return

        # NACK
        if headerParams[1] == 2:
            self.sendMsgAgain(self.lastMsg, 1)
            return

        # ACK file
        if headerParams[1] == 1 and self.fragments != None:
            if self.timers["msg"]:
                self.timers["msg"].kill() # Stop timer


            if len(self.fragments) == self.fragNum:
                self.fragments = None
                self.send(b'', SocketHeader(0, 4, self.fragNum, b''))
                self.timers["msg"] = TimerMsg(self, 4, b'')
                return
            header = SocketHeader(len(self.fragments[self.fragNum]), 1, self.fragNum+1, self.fragments[self.fragNum])
            self.lastMsg = self.fragments[self.fragNum]

            # generovanie chyby
            # NEMAZAT!!!
            # if self.fragNum == 2 :
            #     self.send( createError(self.fragments[self.fragNum] + header.header),  header)
            #     self.timers["msg"] = TimerMsg(self, 1, self.fragments[self.fragNum])
            #     return

            self.send(self.fragments[self.fragNum], header)
            self.timers["msg"] = TimerMsg(self, 1, self.fragments[self.fragNum])
            self.fragNum += 1


    def sendMsgAgain(self, msg, flag):
        self.send(msg, SocketHeader(len(msg), flag, self.fragNum, msg))


    def start3WayHandshake(self):
        if not self.send(b'', SocketHeader(0, 4,0, b'')):
            return False
        try:
            msg, address = self.client.recvfrom(BUFFSIZE)
        except:
            return False

        headerParams = translateHeader(msg[:HEADERSIZE])
        # print(headerParams)

        self.send(b'', SocketHeader(0, 1, 1, b''))
        self.CONNECTED = True

        self.timers["alive"] = TimerAlive(self)
        self.timers["refresh"] = TimerRefresh(self)
        self.timers["alive"].start()
        self.timers["refresh"].start()
        return True


    def switchClients(self):
        self.send(b'', SocketHeader(0, 32,0, b''))
        self.timers["switch"] = TimerMsg(self, 32, b'', 0.5)
        # TODO este otestovat


    def endConnection(self):
        self.send(b'', SocketHeader(0, 64,0, b''))
        #Todo timer



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







