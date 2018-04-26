import re
import subprocess
import time
from hashlib import sha256

import requests

from block import Block
from consensus import get_longest_chain, get_target
from dao import DAO

db = DAO()
self_ip = requests.get('http://httpbin.org/ip').json()['origin']


def get_chain():
    local = db.get_chain()
    remote = []
    return get_longest_chain(remote + [local])


def append_block(block):  #添加区块
    chain = get_chain()
    h = sha256()
    h.update('{}{}{}'.format(chain[-1], block, block.nonce).encode('utf8'))
    if int(h.hexdigest(), 16) < get_target(chain):
        db.append_block(block)
        for nb in get_neighbours():  #遍历邻居节点
            if self_ip not in nb:
                try:
                    requests.post('{}/blocks'.format(nb), json=block.__dict__, timeout=1)     #nb 邻居ip地址
                except:
                    pass
    else:
        print('reject block: {}'.format(block.__dict__))
        print('solution: {} target: {}'.format(h.hexdigest(), hex(get_target(chain))))


def sync_chain():   #同步最长链
    while True:
        chain = db.get_chain()
        for nb in get_neighbours():
            r = requests.get('{}/height'.format(nb), timeout=2)
            if r.json()['height'] > len(chain):
                r = requests.get('{}/blocks'.format(nb), timeout=2)   #请求回复 区块list
                chain = [
                    Block(
                        data['index'], data['timestamp'], data['data'], data['prev_hash'],
                        data['target'], nonce=data['nonce'])
                    for data in r.json()      #json转换Block       #  列表生成
                ]
                db.dump_chain(chain)   #DAO 保存到磁盘
                print('refreshed chain from {}'.format(nb))
        time.sleep(1)


def find_neighbour():    #发现邻居
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


def add_addr(host):  #添加邻居到数据库
    db.add_addr(host)


def get_neighbours():   # 获取所有相邻节点
    nb = set(db.get_neighbours())
    nb.add('http://198.199.100.231:5001')
    return nb
