import hashlib as hasher


VERSION = 0


class Block:
    def __init__(self, **kwargs):
        self.index = kwargs['index']
        self.version = kwargs.get('version', VERSION)
        self.timestamp = kwargs['timestamp']
        self.data = kwargs['data']
        self.prev_hash = kwargs['prev_hash']
        self.difficulty = kwargs['difficulty']
        self.hash = self.hash_block()
        self.nonce = kwargs.get('nonce')

    def hash_block(self):
        sha = hasher.sha256()
        sha.update(str(self).encode('utf8'))
        return sha.hexdigest()

    def __str__(self):
        return '{}{}{}{}{}'.format(
            self.index, self.timestamp, self.data, self.prev_hash, self.difficulty)


class BlockManager:
    def __init__(self):
        pass


GENISIS_BLOCK = {
    "index": 0,
    "version": 0,
    "timestamp": 1524685930.1270132,
    "data": "Hello world:)",
    "prev_hash": "0",
    "difficulty": 1,
    "hash": "0bb19c9b5c043d68da054154e98516acb53018cffaec728b4729dc63d4da07af",
    "nonce": 0
}


def create_genesis_block():
    return GENISIS_BLOCK
