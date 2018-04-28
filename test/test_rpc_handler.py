from asyncio.coroutines import coroutine
import unittest
from unittest import mock

from . import run_async
from .context import toychain
from toychain.dao import DAO
from toychain.rpc import handler


dao = DAO()


class RPCTestCase(unittest.TestCase):
    def setUp(self):
        self.ws = mock.Mock()
        self.ws.remote_address = ('0.0.0.0', '8193')

    def test_on_version(self):
        data = {'ws': self.ws}
        run_async(handler.on_version, data)
        nbs = dao.get_neighbours()
        self.assertIn('{}:{}'.format(*data['ws'].remote_address), nbs)

    def test_on_addr(self):
        host = '0.0.0.0'
        port = 3829
        data = {'data': {'host': host, 'port': port}}
        run_async(handler.on_addr, data)
        nbs = dao.get_neighbours()
        self.assertIn('{}:{}'.format(host, port), nbs)

    def test_on_getaddr(self):
        sendfunc = mock.Mock()
        mock_send = mock.Mock(side_effect=coroutine(sendfunc))
        mock_peer = mock.Mock()
        mock_peer.send = mock_send
        run_async(handler.on_getaddr, {'peer': mock_peer})
        sendfunc.assert_called_once()
