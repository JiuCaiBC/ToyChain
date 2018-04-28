import asyncio
import json
import logging

from toychain import dao
from .block import Block, GENISIS_BLOCK

dao = dao.DAO()
logger = logging.getLogger()


class Chain:
    def __init__(self):
        self.chain = []
        # self.block_queue = asyncio.Queue()
        # self.transaction_queue = asyncio.Queue()

    def build_chain(self, blocks_data):
        for data in blocks_data:
            self.append_block(Block(**data))

    def validate_block(self, prev_block, block):
        if not block.hash == block.hash_block():
            return False
        if not prev_block.hash == block.prev_hash:
            return False
        if not prev_block.index + 1 == block.index:
            return False
        # TODO check difficulty
        # TODO check nonce
        return True

    def append_block(self, block):
        if not self.chain and is_genisis_block(block):
            self.chain.append(block)
            dao.dump_chain([block.__dict__ for block in self.chain])
            logger.info('Appended block {}'.format(block.__dict__))
            return True
        elif self.validate_block(self.chain[-1], block):
            self.chain.append(block)
            dao.dump_chain([block.__dict__ for block in self.chain])
            logger.info('Appended block {}'.format(block.__dict__))
            return True
        else:
            logger.info('Rejected block {}'.format(block.__dict__))
            return False

    def get_block(self, block_hash):
        for block in self.chain:
            if block.hash == block_hash:
                return block

    def get_height(self):
        return len(self.chain)


class ChainManager:
    def __init__(self, chain):
        self.chain = chain
        self.transactions = dict()

        self.chain_handlers = {
            'getblocks': self.on_getblocks,
            'blocks': self.on_blocks,
            'getblock': self.on_getblock,
            'block': self.on_block,
            'getheight': self.on_getheight,
            'height': self.on_height,
            'inv': self.on_inv,
            'tx': self.add_transaction
        }
        self.rpc_queue = None

    async def init(self):
        self.rpc_queue = asyncio.Queue()

    async def start(self):
        await self.init()
        while True:
            if not self.rpc_queue:  # initialization of self.rpc_queue could take a little time
                await asyncio.sleep(2)
            rpc = await self.rpc_queue.get()
            await self.chain_handlers[rpc['method']](rpc)
            self.rpc_queue.task_done()

    async def init_queue(self):
        # Workaround for using sanic as entrance
        self.rpc_queue = asyncio.Queue()

    async def on_getblocks(self, rpc):
        await rpc['peer'].send(json.dumps({
            'method': 'blocks',
            'data': [block.__dict__ for block in self.chain.chain]
        }))

    async def on_blocks(self, rpc):
        for block_data in rpc['data']:
            self.chain.append_block(Block(**block_data))

    async def on_getblock(self, rpc):
        hash_ = rpc['data']
        block = self.chain.get_block(hash_)
        if block:
            await rpc['peer'].send(json.dumps({'method': 'block', 'data': block.__dict__}))

    async def on_block(self, rpc):
        self.chain.append_block(Block(**rpc['data']))

    async def on_getheight(self, rpc):
        await rpc['peer'].send(json.dumps({'method': 'height', 'data': self.chain.get_height()}))

    async def on_height(self, rpc):
        local_height = self.chain.get_height()
        remote_height = rpc['data']
        if local_height < remote_height:
            await rpc['peer'].send(json.dumps({
                'method': 'getblocks',
            }))

    async def on_inv(self, rpc):
        if rpc['data']['type'] == 'block':
            for hash_ in rpc['data']['data']:
                if not self.chain.get_block(hash_):
                    await rpc['peer'].send(json.dumps({'method': 'getblock', 'data': hash_}))
        elif rpc['inv']['type'] == 'transaction':
            pass

    def add_transaction(self, transaction):
        self.transactions[transaction.hash] = transaction


def is_genisis_block(block):
    return block.__dict__ == GENISIS_BLOCK


chain_mgr = ChainManager(Chain())
