import asyncio
import async_timeout
import json
import logging
import os
import sys
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

import uvloop
import websockets

from dao import DAO
from rpc import app
from rpc.server import ws_handler
from rpc.handler import chain_mgr, peer_mgr
from miner import Miner


dao = DAO()
FORMAT = '%(asctime)-15s %(levelname)s %(module)s %(message)s'
# FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def sync_chain():
    while True:
        for peer in peer_mgr.get_peers():
            print('sync {}'.format(str(peer)))
            await peer.send(json.dumps({'method': 'getheight'}))
        await asyncio.sleep(1)


async def advertise_self():
    for peer in peer_mgr.get_peers():
        try:
            # print('connecting ', peer
            with async_timeout.timeout(2):
                ws = await websockets.connect('ws://{}/ws'.format(peer))
            await ws.send(json.dumps({
                'method': 'version',
                'host': '--',
                'port': 5001
            }))
            # print('connected {}'.format(peer))
            asyncio.ensure_future(ws_handler(ws))
        except Exception as e:
            print(e)
            print('Connection to {} failed'.format(peer))


def main():
    chain_mgr.chain.build_chain(dao.get_chain())
    if sys.argv[1] == 'miner':
        miner = Miner(chain_mgr, peer_mgr)
        app.add_task(miner.start)
    app.add_task(sync_chain)
    app.add_task(advertise_self)
    app.add_task(chain_mgr.start)
    app.add_task(peer_mgr.start)
    app.run(host='0.0.0.0', port=5001)


if __name__ == '__main__':
    main()
