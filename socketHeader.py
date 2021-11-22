FORMAT = 'utf-8'
HEADERSIZE = 19
import zlib

class SocketHeader:
    def __init__(self, dataSize, fragNum, flag, data):
        size = dataSize.to_bytes(2, "big")
        fragNum = fragNum.to_bytes(12, "big")
        flag = flag.to_bytes(1, "big")
        self.header = size + fragNum + flag
        self.header += self.addChecksum(data)

    def addChecksum(self, data):
        # s = zlib.crc32(dataSize)
        # fr = zlib.crc32(fragNum)
        # fl = zlib.crc32(flag)
        # d = zlib.crc32(data)
        ch = zlib.crc32(self.header+data)
        print(ch, "adding........")
        y = ~ch
        y = ch.to_bytes(4, "big")

        return y
