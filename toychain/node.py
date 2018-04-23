import re
import subprocess
import time
from hashlib import sha256

import requests

from block import Block
from consensus import get_longest_chain, get_target
from dao import DAO

db = DAO()


def get_chain():
    local = db.get_chain()
    remote = []
    return get_longest_chain(remote + [local])


def append_block(block):
    chain = get_chain()
    h = sha256()
    h.update('{}{}{}'.format(chain[-1], block, block.nonce).encode('utf8'))
    if int(h.hexdigest(), 16) < get_target(chain):
        db.append_block(block)

    for nb in get_neighbours():
        requests.post('{}/blocks'.format(nb), json=block.__dict__, timeout=2)


def sync_chain():
    while True:
        chain = db.get_chain()
        for nb in get_neighbours():
            r = requests.get('{}/height'.format(nb), timeout=2)
            if r.json()['height'] > len(chain):
                r = requests.get('{}/blocks'.format(nb), timeout=2)
                chain = [
                    Block(
                        data['index'], data['timestamp'], data['data'], data['prev_hash'],
                        nonce=data['nonce'])
                    for data in r.json()
                ]
                db.dump_chain(chain)
                print('refreshed chain from {}'.format(nb))
        time.sleep(1)


def find_neighbour():
    def localhosts():
        res = subprocess.check_output(['arp', '-a']).decode('utf8')
        localhosts = [
            'http://{}:5001'.format(ip)
            for ip in re.findall(r'192\.168\.[0-9]+\.[0-9]+', res) if '255' not in ip
        ]
        localhosts.append('http://198.199.100.231:5001')
        return localhosts

    for localhost in localhosts():
        try:
            r = requests.get(localhost, params={'msg': '天王盖地虎'}, timeout=1)
        except requests.exceptions.ConnectionError:
            continue

        if r.text == '宝塔镇河妖':
            print('found node {}'.format(localhost))
            add_addr(localhost)
        else:
            print('remove {}'.format(localhost))
            db.remove_neighbour(localhost)


def add_addr(host):
    db.add_addr(host)


def get_neighbours():
    nb = set(db.get_neighbours())
    nb.add('http://198.199.100.231:5001')
    return nb
