import asyncio
import json
import logging
import time
from hashlib import sha256

from chain import Block
from chain import consensus


logger = logging.getLogger()


class Miner:
    def __init__(self, chain_manager, peer_manager):
        self.chain_mgr = chain_manager
        self.peer_mgr = peer_manager

    def pop_transaction(self):
        if not self.chain_mgr.transactions:
            return
        _, tx = self.chain_mgr.transactions.popitem()
        return tx

    async def proof_of_work(self):
        nonce = 0
        tx = None
        while True:
            h = sha256()
            difficulty = consensus.get_difficulty(self.chain_mgr.chain.chain)
            target = consensus.STANDARD_TARGET / difficulty
            prev_block = self.chain_mgr.chain.chain[-1]
            if not tx:
                # Poll transaction updates
                tx = self.pop_transaction()
            block = Block(**{
                'index': prev_block.index + 1,
                'timestamp': time.time(),
                'data': {'transactions': [tx.__dict__]} if tx else 'mining test',
                'prev_hash': prev_block.hash,
                'difficulty': difficulty,
            })

            logger.info('Tx: {}'.format(tx))
            h.update('{}{}{}'.format(prev_block, block, nonce).encode('utf8'))
            hash_value = int(h.hexdigest(), 16)
            logger.info('Hashed block{}@ difficulty={} nonce={} result={}'.format(
                block.index, difficulty, nonce, h.hexdigest()
            ))

            if hash_value < target:
                logger.info('solution found! {} @ target: {}, index: {}'.format(
                    nonce, target, block.index))
                block.nonce = nonce
                return block
            await asyncio.sleep(1)  # 1h/s
            nonce += 1

    async def start(self):
        async def mine():
            while True:
                block = await self.proof_of_work()
                appended = self.chain_mgr.chain.append_block(block)
                if not appended:
                    continue

                # advertise new mined block
                for peer in self.peer_mgr.get_peers():
                    await peer.send(json.dumps({
                        'method': 'inv',
                        'data': {'type': 'block', 'data': [block.hash]}
                    }))
        logger.info('miner started')
        asyncio.ensure_future(mine())
