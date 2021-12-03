import zlib
import random

FORMAT = 'utf-8'
HEADERSIZE = 11
#MAX_FRAGMENT_SIZE = 1500 - HEADER_SIZE - 20 - 8 #1500 (max data on Link layer) - my header - ip header (20B) - UDP header (8B)

# format na | Size 3B | Flag 1B | Frag number 3B | Checksum 4B | Data...
class SocketHeader:
    def __init__(self, dataSize, flag, fragN, data):
        size = (dataSize+HEADERSIZE).to_bytes(3, "big")
        flag = flag.to_bytes(1, "big")
        if fragN == None:
            fragN = 0
        fragN = fragN.to_bytes(3, "big")
        self.header = size + flag + fragN
        self.header += self.addChecksum(data)


    def addChecksum(self, data):
        ch = zlib.crc32(self.header+data)
        y = ch.to_bytes(4, "big")
        return y


def translateHeader(headerBits):
    size = int.from_bytes(headerBits[:3], "big")
    flag = int.from_bytes(headerBits[3:4], "big")
    fragN = int.from_bytes(headerBits[4:7], "big")
    return [size, flag, fragN]



def checkChecksum(data):
    ch = data[7: HEADERSIZE]
    x = data[:7] + data[HEADERSIZE: ]
    y = zlib.crc32(x)
    a = int.from_bytes(ch, "big")
    t = a^y
    if t == 0:
        return True
    return False

def createError(msg):
    data = msg[HEADERSIZE:]
    size, flag, fragN = translateHeader(msg[:HEADERSIZE])
    if size > 5:
        r = random.randint(1, size-2)
    else:
        r = 1
    data = data[:r-1] + b'00' + data[r:]
    return data

#TODO
# -timeout cez posielanie suboru nema bezat
# -velkosť správ súboru, Ok
# -všetky správy majú frag num, ok
# -fragmentácia aj mena súboru, ok
# -posielanie txt sprav, ok
# -NACK vypisuje nespravne msg num