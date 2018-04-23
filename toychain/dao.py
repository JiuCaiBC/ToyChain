import json

from block import Block, create_genesis_block


class DAO:
    def __init__(self, db_path=None, nb_db_path=None):
        if db_path:
            self.db_path = db_path
            self.nb_db_path = nb_db_path
        else:
            self.db_path = './chain.json'
            self.nb_db_path = './neighbours.json'

    def get_chain(self):
        try:
            with open(self.db_path, 'r') as f:
                chain = json.load(f)
            chain = [
                Block(
                    block['index'], block['timestamp'], block['data'], block['prev_hash'],
                    block['target'], nonce=block['nonce'])
                for block in chain]
        except:
            chain = [create_genesis_block()]
            self.dump_chain(chain)

        return chain

    def get_block(self, block_hash):
        chain = self.get_chain()
        block = [block for block in chain if block.hash == block_hash]
        return block[0]

    def append_block(self, block):
        chain = self.get_chain()
        if block.index == chain[-1].index + 1:
            chain.append(block)
            self.dump_chain(chain)

    def dump_chain(self, chain):
        with open(self.db_path, 'w+') as f:
            json.dump([block.__dict__ for block in chain], f, indent=4)

    def add_addr(self, addr):
        with open(self.nb_db_path, 'r') as f:
            neighbours = json.load(f)
        neighbours.append(addr)
        with open(self.nb_db_path, 'w+') as f:
            json.dump(neighbours, f)

    def dump_neighbours(self, neighbours):
        with open(self.nb_db_path, 'w+') as f:
            json.dump(neighbours, f)

    def get_neighbours(self):
        try:
            with open(self.nb_db_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def remove_neighbour(self, neighbour):
        neighbours = self.get_neighbours()
        neighbours.remove(neighbour)
        self.dump_neighbours(neighbours)
