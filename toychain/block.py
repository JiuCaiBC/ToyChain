import hashlib as hasher
import time


VERSION = 0


class Block:
    def __init__(self, index, timestamp, data, prev_hash, nonce=None, version=VERSION):
        self.index = index
        self.version = version
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.hash_block()
        self.nonce = nonce

    def hash_block(self):
        sha = hasher.sha256()
        sha.update(str(self).encode('utf8'))
        return sha.hexdigest()

    def __str__(self):
        return '{}{}{}{}'.format(self.index, self.timestamp, self.data, self.prev_hash)


def create_genesis_block():
    return Block(0, time.time(), 'Hello world:)', '0', 0)
