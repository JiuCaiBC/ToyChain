import asyncio
import json
import logging

import async_timeout
import websockets

from toychain.dao import DAO

dao = DAO()
logger = logging.getLogger()


class Peer:
    def __init__(self, addr, connection=None):
        self.addr = addr
        assert not isinstance(connection, int)
        self.connection = connection
        self.conn_lock = asyncio.Lock()

    async def get_connection(self):
        if not self.conn_lock:
            await asyncio.sleep(5)  # wait app to start up
        try:
            await self.conn_lock.acquire()
            return await self._connection()
        except Exception as e:
            logger.error(e, exc_info=True)
        finally:
            self.conn_lock.release()

    async def _connection(self):
        from ..rpc.server import ws_handler
        if not self.connection:
            try:
                with async_timeout.timeout(2):
                    logger.info('Sonnecting {}'.format(self.addr))
                    self.connection = await websockets.connect('ws://{}/ws'.format(self.addr))
                    asyncio.ensure_future(ws_handler(self.connection))
            except Exception as e:
                logger.error(e)
                logger.info('Connection to {} timeout'.format(self.addr))
                peer_mgr.remove_peer(self.addr)

        return self.connection

    async def send(self, data):
        ws = await self.get_connection()
        if not ws:
            logger.warning('Abort rpc. No connection.')
            return

        try:
            await ws.send(data)
            logger.debug('Send {}'.format(data))
        except websockets.exceptions.ConnectionClosed:
            self.connection = None
            await self.get_connection()

    def __str__(self):
        return self.addr


class PeerManager:
    def __init__(self):
        self.peers = dict()

    async def init(self):
        seed = '198.199.100.231:5001'
        for addr in dao.get_neighbours():
            self.peers[addr] = Peer(addr)
        self.peers[seed] = Peer(seed)
        logger.info('loaded peers: {}'.format(list(self.peers.keys())))

    def add_peer(self, addr, connection=None):
        peer = None
        if addr in self.peers:
            peer = self.peers[addr]
            peer.connection = connection if connection else peer.connection
        else:
            peer = Peer(addr, connection=connection)
            self.peers[addr] = peer
            dao.add_addr(str(peer))
            logger.info('Add peer {}'.format(peer))

        return peer

    def remove_peer(self, addr):
        dao.remove_neighbour(addr)
        if addr in self.peers:
            del self.peers[addr]

    def get_peers(self):
        return list(self.peers.values())

    async def start(self):
        await self.init()
        while True:
            for peer in list(self.peers.values()):  # peers could change size during the loop
                try:
                    logger.info('ping {}'.format(peer))
                    await peer.send(json.dumps({'method': 'ping'}))
                except Exception as e:
                    logger.error(e, exc_info=True)
                    logger.info('Removing peer {}'.format(peer))
                    self.remove_peer(peer.addr)

            await asyncio.sleep(60)


peer_mgr = PeerManager()
