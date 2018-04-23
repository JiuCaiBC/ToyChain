import time
from hashlib import sha256
from threading import Thread

from block import Block
from consensus import get_target
from node import append_block, get_chain, find_neighbour, sync_chain


def proof_of_work():
    nonce = 0
    while True:
        h = sha256()
        target = get_target(get_chain())
        prev_block = get_chain()[-1]
        block = Block(
            prev_block.index + 1, time.time(), miner + ' mining test', prev_block.hash, hex(target))
        h.update('{}{}{}'.format(prev_block, block, nonce).encode('utf8'))
        res = int(h.hexdigest(), 16)
        print(res)
        if res < target:
            print('solution found! {} @ target: {}'.format(nonce, hex(target)))
            block.nonce = nonce
            return block
        time.sleep(1)  # 1h/s
        nonce += 1

import requests
miner = requests.get('https://randomuser.me/api/').json()['results'][0]['login']['username']
def mine():
    block = proof_of_work()
    append_block(block)


def main():
    # neighbour_worker = Thread(target=find_neighbour, daemon=False)
    sync_workder = Thread(target=sync_chain, daemon=False)
    # neighbour_worker.start()
    sync_workder.start()
    while True:
        mine()

if __name__ == '__main__':
    main()
