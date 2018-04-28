import json
import os
import sys
import unittest
from unittest import mock
from asyncio.coroutines import coroutine

from .context import resource_dir, toychain
from . import run_async
from toychain.chain.chain import ChainManager, Chain
from toychain.chain import Block


with open('{}/chain.json'.format(resource_dir), 'r') as f:
    chain_data = json.load(f)


class BlockTestCase(unittest.TestCase):
    def test_hash(self):
        block = Block(**chain_data[0])
        self.assertIsNotNone(block.hash_block())


class ChainTestCase(unittest.TestCase):
    def setUp(self):
        self.chain = Chain()

    def test_build_chain(self):
        self.chain.build_chain(chain_data)
        self.assertEqual(len(chain_data), self.chain.get_height())

    def test_append_block(self):
        self.chain.build_chain(chain_data[:1])
        for data in chain_data[1:]:
            self.chain.append_block(Block(**data))

        self.assertEqual(len(chain_data), self.chain.get_height())
        # test appending an invalid block
        self.assertFalse(self.chain.append_block(Block(**chain_data[0])))

    def test_getblock(self):
        self.chain.build_chain(chain_data)
        block = self.chain.get_block(chain_data[0]['hash'])
        self.assertIsNotNone(block)

    def test_validate_block(self):
        self.chain.build_chain(chain_data[:1])
        block0 = Block(**chain_data[0])
        block1 = Block(**chain_data[1])
        self.assertTrue(self.chain.validate_block(block0, block1))

        block1.prev_hash += 'uselesstail'
        self.assertFalse(self.chain.validate_block(block0, block1))

        block1 = Block(**chain_data[1])
        block1.prev_hash += 'uselesstail'
        self.assertFalse(self.chain.validate_block(block0, block1))

    def tes_getheight(self):
        self.chain.build_chain(chain_data)
        self.assertTrue(self.chain.get_height(), len(chain_data))


class ChainManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.mgr = ChainManager(Chain())
        self.mock_peer = mock.Mock()
        self.mock_sendfunc = mock.Mock()
        self.mock_peer.send = mock.Mock(side_effect=coroutine(self.mock_sendfunc))

    def test_on_getblocks(self):
        run_async(self.mgr.on_getblocks, {'peer': self.mock_peer})
        self.mock_sendfunc.assert_called_once()

    def test_on_blocks(self):
        run_async(self.mgr.on_blocks, {'data': chain_data})
        self.assertEqual(self.mgr.chain.get_height(), len(chain_data))

    def test_on_getblock(self):
        run_async(self.mgr.on_getblock, {'data': 'fakehash', 'peer': self.mock_peer})
        self.mock_sendfunc.assert_not_called()
        run_async(self.mgr.on_getblock, {'data': chain_data[0]['hash'], 'peer': self.mock_peer})
        self.mock_sendfunc.assert_not_called()

    def test_on_block(self):
        run_async(self.mgr.on_block, {'data': chain_data[0]})
        self.assertEqual(self.mgr.chain.get_height(), 1)

    def test_on_getheight(self):
        self.mgr.chain.build_chain(chain_data)
        run_async(self.mgr.on_getheight, {'peer': self.mock_peer})
        self.mock_sendfunc.assert_called_with(json.dumps({'method': 'height', 'data': 94}))

    def test_on_height(self):
        self.mgr.chain.build_chain(chain_data[:1])
        run_async(self.mgr.on_height, {'peer': self.mock_peer, 'data': 10})
        self.mock_sendfunc.assert_called_with(json.dumps({'method': 'getblocks'}))

    def test_inv(self):
        self.mgr.chain.build_chain(chain_data[:1])
        run_async(self.mgr.on_inv, {
            'peer': self.mock_peer,
            'data': {
                'type': 'block',
                'data': [block['hash'] for block in chain_data]
            }})
        self.assertEqual(self.mock_sendfunc.call_count, len(chain_data) - 1)
