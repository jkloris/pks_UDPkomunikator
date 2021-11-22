FORMAT = 'utf-8'
HEADERSIZE = 10
import zlib

# format: | size 2B | window 3B | Flag 1B | Checksum 4B | Data...
class SocketHeader:
    def __init__(self, dataSize, window, flag, data):
        size = (dataSize+HEADERSIZE).to_bytes(2, "big")
        window = window.to_bytes(3, "big")
        flag = flag.to_bytes(1, "big")
        self.header = size + window + flag
        self.header += self.addChecksum(data)

    def addChecksum(self, data):
        ch = zlib.crc32(self.header+data)
        y = ~ch
        y = ch.to_bytes(4, "big")
        return y


def translateHeader(headerBits):
    size = int.from_bytes(headerBits[:2], "big")
    window = int.from_bytes(headerBits[2:5], "big")
    flag = int.from_bytes(headerBits[5:6], "big")
    return [size, window, flag]



def checkChecksum(data):
    ch = data[6:10]
    x = data[:6] + data[10:]
    y = zlib.crc32(x)
    a = int.from_bytes(ch, "big")
    t = a^y
    # print(y,a,t, "checking#####")
    if t == 0:
        return True
    return False