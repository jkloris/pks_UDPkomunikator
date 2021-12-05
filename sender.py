import socket
from socketHeader import *
from timers import *

BUFFSIZE  = 1472
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
        self.fragNum = 0
        self.fragments = {
            "file" : None,
            "name" : None,
            "flag" : None
        }
        self.lastMsg = None
        self.msgNum = 2
        self.lastAck = 0



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

    # @param filepath je cesta k suboru respektive string posielanej spravy. Zalezi od type
    # @param type: druh posielanej spravy; 1 = subor, 2 = string
    def startSendingFile(self, filename, filepath, fragsize, type):
        if type == 1:
            self.fragments["file"] = chunkFile(filepath, fragsize)
        elif type == 2:
            self.fragments["file"] = chunkString(filepath, fragsize)

        self.fragments["name"] = chunkString(filename, fragsize)
        self.lastMsg = self.fragments["name"][0]
        self.fragments["flag"] = "name"

        self.send(self.lastMsg, SocketHeader(len(self.lastMsg), 1, self.msgNum, self.lastMsg))
        self.timers["msg"] = TimerMsg(self, 1, self.lastMsg, self.msgNum)

        self.fragNum = 0
        self.msgNum+=1


    def loop(self):
        while self.CONNECTED:
            msg, address = self.client.recvfrom(BUFFSIZE)

            if self.timers["msg"]:
                self.timers["msg"].kill()
                self.timers["msg"] = None

            self.handleMsg(msg, address)

    # spracovanie sprav
    # msg je sprava
    def handleMsg(self, msg, address):
        headerParams = translateHeader(msg[:HEADERSIZE])
        print(f"[Klient] Msg from {address}:  [Segment Size: {headerParams[0]}B, Flag: {headerParams[1]}, Segment num: {headerParams[2]}]")


        if not checkChecksum(msg):
            print("TODO Sending NACK")  # TODO

        if not self.CONNECTED:
            return

            # NACK
        if headerParams[1] == 2:
            self.sendMsgAgain(self.lastMsg, 1, headerParams[2])
            # if self.timers["msg"]:
            #     self.timers["msg"].kill()
            return

        # REFRESH + ACK
        if headerParams[1] == 17:
            self.timers["alive"].refreshTime()
            return

        # SWITCH + ACK
        if headerParams[1] == 33:
            # TODO zisti preco je NONE a otestovat
            # self.timers["switch"].kill()
            self.send(b'', SocketHeader(0, 33, self.msgNum, b''))
            self.msgNum+=1
            from socketComunicator import closeClientOpenServer
            closeClientOpenServer(self)
            return

        if headerParams[1] == 65:
            # todo start timer
            self.send(b'', SocketHeader(0, 65, self.msgNum, b''))
            self.msgNum+=1
            from socketComunicator import disconnectClient
            disconnectClient(self)
            return

        if self.lastAck >= headerParams[2]:
            return

        # FIN + ACK
        if headerParams[1] == 9:
            # if self.timers["msg"]:
            #     self.timers["msg"].kill()
            self.timers["alive"].refreshTime()
            self.timers["refresh"].unpause()
            self.lastAck = headerParams[2]
            return



        # prijatie mena suboru + ACK
        if headerParams[1] == 129:
            self.lastAck = headerParams[2]
            self.fragments["name"] = None
            self.fragments["flag"] = "file"
            header = SocketHeader(len(self.fragments["file"][0]), 1, self.msgNum, self.fragments["file"][0])
            self.send(self.fragments["file"][0], header)
            self.msgNum+=1
            self.fragNum = 0
            return

        # ACK file
        if headerParams[1] == 1 and self.fragments["file"] != None:
            self.lastAck = headerParams[2]
            self.fragNum += 1
            # if self.timers["msg"]:
            #     self.timers["msg"].kill() # Stop timer

            if self.fragments["name"] != None and len(self.fragments["name"]) == self.fragNum:
                self.send(b'', SocketHeader(0, 128, self.msgNum, b''))
                self.timers["msg"] = TimerMsg(self, 128, b'', self.msgNum)
                self.msgNum += 1
                return

            if self.fragments["name"] == None and len(self.fragments["file"]) == self.fragNum:
                self.fragments["file"] = None
                self.send(b'', SocketHeader(0, 8,  self.msgNum, b''))
                self.timers["msg"] = TimerMsg(self, 8, b'', self.msgNum)
                self.msgNum+=1
                return

            header = SocketHeader(len(self.fragments[self.fragments["flag"]][self.fragNum]), 1, self.msgNum, self.fragments[self.fragments["flag"]][self.fragNum])
            self.lastMsg = self.fragments[self.fragments["flag"]][self.fragNum]

            # generovanie chyby
            # NEMAZAT!!!
            if self.fragNum == 5 :
                self.send( createError(self.fragments[self.fragments["flag"]][self.fragNum] + header.header),  header)
                # self.timers["msg"] = TimerMsg(self, 1, self.lastMsg, self.msgNum)
                self.msgNum += 1
                return

            self.send(self.fragments[self.fragments["flag"]][self.fragNum], header)
            self.timers["msg"] = TimerMsg(self, 1, self.lastMsg, self.msgNum)
            self.msgNum += 1

    def sendMsgAgain(self, msg, flag, msgNum):
        self.send(msg, SocketHeader(len(msg), flag, msgNum, msg))
        return


    def start3WayHandshake(self):
        if not self.send(b'', SocketHeader(0, 4, 0, b'')):
            return False
        self.timers["msg"] = TimerMsg(self, 4, b'', 0)

        try:
            msg, address = self.client.recvfrom(BUFFSIZE)
        except:
            return False
        self.timers["msg"].kill()
        self.timers["msg"].thread.join()
        self.timers["msg"] = None

        headerParams = translateHeader(msg[:HEADERSIZE])
        print(f"[Klient] Msg from {address}:  [Segment Size: {headerParams[0]}B, Flag: {headerParams[1]}, Segment num: {headerParams[2]}]")

        self.send(b'', SocketHeader(0, 1, 1, b''))
        self.CONNECTED = True

        self.timers["alive"] = TimerAlive(self)
        self.timers["refresh"] = TimerRefresh(self)
        self.timers["alive"].start()
        self.timers["refresh"].start()
        return True


    def switchClients(self):
        self.send(b'', SocketHeader(0, 32,self.msgNum, b''))
        # self.timers["switch"] = TimerMsg(self, 32, b'', 0.5, self.msgNum)
        self.msgNum+=1
        # TODO este otestovat


    def endConnection(self):
        self.send(b'', SocketHeader(0, 64, self.msgNum, b''))
        self.msgNum+=1
        #Todo timer



# Rozdeli subor do bit casti podla velkosti fragmentu
# @return colletion: list casti
def chunkFile(file, buffsize):
    # buffsize -= HEADERSIZE
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
    # buffsize -= HEADERSIZE
    for i in range(0, len(string), buffsize):
        collection.append(string[i:i+buffsize].encode(FORMAT))
    return collection







