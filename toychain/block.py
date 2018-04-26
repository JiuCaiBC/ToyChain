import hashlib as hasher
import time


VERSION = 0


class Block:                            #一个Block的类 里面定义了—init，hash—block，str 函数，包含区块的信息
    def __init__(self, index, timestamp, data, prev_hash, nonce=None, version=VERSION): #定义初始化参数
        self.index = index
        self.version = version
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.hash_block()
        self.nonce = nonce

    def hash_block(self):# 定义hash-block函数
        sha = hasher.sha256()     #hasher里面的sha256方法
        sha.update(str(self).encode('utf8'))   #？？？
        return sha.hexdigest()                 #定义进制

    def __str__(self):
        return '{}{}{}{}'.format(self.index, self.timestamp, self.data, self.prev_hash)  #？？？{}的使用方法


def create_genesis_block():     #创建原始区块
    return Block(0, time.time(), 'Hello world:)', '0', 0)
