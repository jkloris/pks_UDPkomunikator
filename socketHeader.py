FORMAT = 'utf-8'
HEADERSIZE = 19

class SocketHeader:
    def __init__(self, dataSize, fragNum, flag):
      size = dataSize.to_bytes(2,"big")
      fragNum = fragNum.to_bytes(16, "big")
      flag = flag.to_bytes(1, "big")
      self.header = size+fragNum+flag
