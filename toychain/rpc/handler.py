import asyncio
import json

from toychain.chain import Block, Transaction, chain_mgr
from toychain.dao import DAO
from toychain.peer import peer_mgr

dao = DAO()
loop = asyncio.get_event_loop()


async def handle(data):
    if 'ws' in data:
        peer = peer_mgr.add_peer('{}:{}'.format(*data['ws'].remote_address), connection=data['ws'])
        data['peer'] = peer
    method = data['method']
    if method in handlers:
        await handlers[method](data)
    else:
        await chain_mgr.rpc_queue.put(data)


async def on_version(rpc):
    peer_mgr.add_peer('{}:{}'.format(*rpc['ws'].remote_address))


async def on_addr(rpc):
    peer_mgr.add_peer('{}:{}'.format(rpc['data']['host'], rpc['data']['port']))


async def on_getaddr(data):
    seed = 'localhost:5001'
    if seed not in peer_mgr.peers:
        peer_mgr.add_peer(seed)
    await data['peer'].send(json.dumps({
        'method': 'addr',
        'data': [str(peer) for peer in peer_mgr.get_peers()]
    }))


async def on_ping(rpc):
    await rpc['peer'].send(json.dumps({'method': 'pong'}))


async def pong(_):
    pass


# async def on_transaction(data):
#     chain_mgr.add_transaction(data['data'])
#     for peer in peer_mgr.peers.values():
#         if peer == data['peer']:
#             continue

#         await peer.send(json.dumps({
#             'method': 'inv',
#             'data': {
#                 'type': 'transaction',
#                 'data': [data['data']]
#             }
#         }))


async def handle_transaction(transaction):  # temp
    tx = Transaction(
        transaction['sender'], transaction['receiver'], transaction['amount'])
    chain_mgr.add_transaction(tx)


handlers = {
    'version': on_version,
    'addr': on_getaddr,
    'getaddr': on_getaddr,
    'ping': on_ping,
    'pong': pong,
    # 'tx': on_transaction
}
