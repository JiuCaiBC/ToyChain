import json
from chain.block import GENISIS_BLOCK


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
        except Exception as e:
            print(e)
            chain = [GENISIS_BLOCK]
            self.dump_chain(chain)

        return chain

    def get_block(self, block_hash):
        chain = self.get_chain()
        block = [block for block in chain if block['hash'] == block_hash]
        if block:
            return block[0]

    def append_block(self, block):
        chain = self.get_chain()
        chain.append(block)
        self.dump_chain(chain)

    def dump_chain(self, chain):
        with open(self.db_path, 'w+') as f:
            json.dump(chain, f, indent=4)

    def add_addr(self, addr):
        neighbours = set(self.get_neighbours())
        neighbours.add(addr)
        with open(self.nb_db_path, 'w+') as f:
            json.dump(list(neighbours), f)

    def dump_neighbours(self, neighbours):
        with open(self.nb_db_path, 'w+') as f:
            json.dump(list(set(neighbours)), f)

    def get_neighbours(self):
        nbs = []
        try:
            with open(self.nb_db_path, 'r') as f:
                nbs = json.load(f)
        except Exception:
            pass

        return nbs

    def remove_neighbour(self, neighbour):
        neighbours = self.get_neighbours()
        try:
            neighbours.remove(neighbour)
        except ValueError:
            pass
        self.dump_neighbours(neighbours)
