import unittest
from unittest import mock
from asyncio.coroutines import coroutine

from . import run_async
from .context import toychain
from toychain.dao import DAO
from toychain.peer import Peer, PeerManager


dao = DAO()


class PeerManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.mgr = PeerManager()
        self.addr = '0.0.0.0:11110'

    def test_add_peer(self):
        self.mgr.add_peer(self.addr)
        peer_addrs = dao.get_neighbours()
        self.assertIn(self.addr, peer_addrs)
        self.assertIn(self.addr, self.mgr.peers)

    def test_remove_peer(self):
        self.mgr.remove_peer(self.addr)
        peer_addrs = dao.get_neighbours()
        self.assertNotIn(self.addr, peer_addrs)
        self.assertNotIn(self.addr, self.mgr.peers)

    def test_get_peers(self):
        self.mgr.add_peer(self.addr)
        self.assertIsNotNone(self.mgr.get_peers())


class PeerTestCase(unittest.TestCase):
    def test_get_connection(self):
        peer = Peer('api.huobipro.com')
        self.assertIsNone(peer.connection)
        result = run_async(peer.get_connection)
        self.assertIsNotNone(result)
        self.assertIsNotNone(peer.connection)

    def test_send(self):
        peer = Peer('api.huobipro.com')
        sendfunc = mock.Mock('sendfunc')
        mock_conn = mock.Mock(side_effect=coroutine(sendfunc))
        mock_conn.send = mock.Mock(side_effect=coroutine(sendfunc))
        peer.get_connection = mock.Mock(side_effect=coroutine(lambda: mock_conn))
        run_async(peer.send, 'msg')
        sendfunc.assert_called_with('msg')
