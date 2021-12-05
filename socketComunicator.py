import socket
from socketHeader import *
from sender import *
from receiver import *
import time
import os.path
from os import path
import datetime

# _PORT = 8880
# dstIP = "192.168.1.13"
FORMAT = 'utf-8'
# FRAGSIZE = 2**10
BUFFSIZE  = 1472

# FILENAME = "pic2.png"
# FILEPATH = "../blbosti/" + FILENAME
ROLE = None

# vypise subory v priecinku @param path
def listFilesInDir(path):
    print("Vyber cislo suboru, ktory chces poslat:")
    for i,f in enumerate(os.listdir(path)):
        print(f"{i}..{f}")
    while True:
        try:
            n = int(input())
            break
        except:
            print("*Invalid Input*")

    return os.listdir(path)[n]

# priebeh spojenia
# sluzi aj ako UI
def restart(x):

    if x == 1:
        while True:
            print("[PRIKAZ] Napis port serveru:")
            try:
                port = int(input())
                break
            except:
                print("[ERROR] *Invalid Input*")

        while True:
            print(f"[PRIKAZ] Zadaj priecinok ukladania suborov")
            filepath = input()
            if path.exists(filepath):
                break
            else:
                print("[ERROR] *Invalid Input*")

        ROLE = Receiver(port, filepath)
        ROLE.start()

    elif x == 2:

        while True:
            print("[PRIKAZ] Napis cielovu IP adresu:")
            dstIP = input()
            try:
               socket.inet_aton(dstIP)
               break
            except:
                print("[ERROR] *Neplatna IP adresa*")



        while True:
            print("[PRIKAZ] Napis cielovy port:")
            try:
                port = int(input())
                break
            except:
                print("[ERROR] *Invalid Port*")


        ROLE = Sender(dstIP, port)
        counter = 0
        while not ROLE.start3WayHandshake():
            time.sleep(0.5)
            counter+=1
            if counter > 10:
                print("[ERROR] Na zadanom porte neexistuje spojenie\n[Klient] *ukoncujem program*")
                ROLE.endConnection()
                return

        print("[Klient] *Spojenie vytvorené*")
        # ROLE.loop(FILENAME, BUFFSIZE)
        loopThread = threading.Thread(target=ROLE.loop)
        loopThread.start()

        while True:
            print("[PRIKAZ]\n0: Poslat spravu\n1: Poslat subor\n2: Koniec\n3: Prehod funkcie")
            try:
                cmd = int(input())
            except:
                cmd = -1
                print("[ERROR]*Invalid Input*")
            if cmd == 0:
                ROLE.timers["alive"].pause()
                ROLE.timers["refresh"].pause()

                while True:
                    print(f"[PRIKAZ] Zadaj velkost fragmentu (1 - {BUFFSIZE - 1 - HEADERSIZE})")
                    try:
                        fragsize = int(input())
                        fragsize = fragsize if fragsize > 0 and fragsize < BUFFSIZE else BUFFSIZE - 1 - HEADERSIZE
                        break
                    except:
                        print("[ERROR] *Invalid Input*")

                print(f"[PRIKAZ] Napis spravu, ktoru chces poslat")
                message = input()

                newname = datetime.datetime.now()
                filename = "msg"+newname.strftime('%H-%M_%d.%m')+".txt"

                fileThread = threading.Thread(target=ROLE.startSendingFile, args=(filename, message, fragsize, 2))
                fileThread.start()
                fileThread.join()
                continue

            elif cmd == 1:
                ROLE.timers["alive"].pause()
                ROLE.timers["refresh"].pause()

                while True:
                    print(f"[PRIKAZ] Zadaj velkost fragmentu (1 - {BUFFSIZE - 1 - HEADERSIZE})")
                    try:
                        fragsize = int(input())
                        fragsize = fragsize if fragsize > 0 and fragsize < BUFFSIZE else BUFFSIZE - 1 - HEADERSIZE
                        break
                    except:
                        print("[ERROR] *Invalid Input*")

                while True:
                    print(f"[PRIKAZ] Zadaj priecinok posielaneho suboru")
                    filepath = input()
                    if path.exists(filepath):
                        break
                    else:
                        print("[ERROR] *Invalid Input*")

                filename = listFilesInDir(filepath)
                filepath = filepath+"/"+filename

                fileThread = threading.Thread(target=ROLE.startSendingFile, args=(filename, filepath, fragsize, 1))
                fileThread.start()
                fileThread.join()
                continue
            elif cmd == 2:
                ROLE.endConnection()
                break
            elif cmd == 3:
                ROLE.switchClients()
                break



if __name__ == "__main__":
    myIP = socket.gethostbyname(socket.gethostname())

    print("[PRIKAZ]\n1...server\n2...client")
    x = int(input())

    restart(x)

# vymena roli zo strany klienta
def closeClientOpenServer(sender):
    port = sender.dstPORT
    sender.closeAllTimers()
    sender.CONNECTED = False
    sender.timers["refresh"].thread.join()
    sender.timers["alive"].thread.join()

    sender.client.close()
    print("------Client closed-------")
    restart(1)

# vymena roli zo strany servera
def closeServerOpenClient(receiver):
    port = receiver.myPORT
    receiver.RUNNING = False
    receiver.server.close()
    print("-----Server closed------")
    restart(2)

# odpoji klienta
def disconnectClient(sender):
    sender.closeAllTimers()
    sender.CONNECTED = False
    sender.timers["refresh"].thread.join()
    sender.timers["alive"].thread.join()
    sender.client.close()
    print("-----Client disconnected------")
    restart(2)

# odpoji server
def disconnectServer(receiver):
    receiver.RUNNING = False
    receiver.server.close()
    print("-----Server disconnected------")
    restart(1)

