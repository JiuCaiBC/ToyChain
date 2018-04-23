import time
from hashlib import sha256
from threading import Thread

from block import Block
from consensus import get_target
from node import append_block, get_chain, find_neighbour, sync_chain


def proof_of_work(prev_block, new_block):
    base = '{}{}'.format(prev_block, new_block)

    nonce = 0
    target = get_target(get_chain())
    while True:
        h = sha256()
        h.update('{}{}'.format(base, nonce).encode('utf8'))
        res = int(h.hexdigest(), 16)
        print(res)
        if res < target:
            print('solution found! {} @ target: {}'.format(nonce, hex(target)))
            return nonce
        time.sleep(1)  # 1h/s
        nonce += 1


def mine():
    prev_block = get_chain()[-1]
    block = Block(prev_block.index + 1, time.time(), 'mining test', prev_block.hash)
    solution = proof_of_work(prev_block, block)
    block.nonce = solution
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
