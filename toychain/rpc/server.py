import asyncio
import json
import logging

from sanic import Sanic
from sanic.response import json as jsonify
from sanic.response import html
import websockets

from .handler import handle, chain_mgr, peer_mgr, handle_transaction

app = Sanic()
logger = logging.getLogger()


async def ws_handler(ws):
    while True:
        try:
            data = await ws.recv()
            logger.debug('Received {}'.format(data))
            rpc_data = json.loads(data)
            rpc_data['ws'] = ws
        except websockets.exceptions.ConnectionClosed:
            peer = peer_mgr.peers['{}:{}'.format(*ws.remote_address)]
            peer.connection = None
            await peer.get_connection()
            return
        except Exception as e:
            logger.error(e, exc_info=True)
            continue
        else:
            await handle(rpc_data)


@app.websocket('/ws')
async def websocket(_, ws):
    await ws_handler(ws)


@app.route('/height')
async def get_height(_):
    return html(chain_mgr.chain.get_height())


@app.route('/blocks')
async def get_blocks(_):
    return jsonify([block.__dict__ for block in chain_mgr.chain.chain])


@app.route('/tx')
async def get_transaction(_):
    return html("""
    <!DOCTYPE html>
    <html>
    <body>

    <div style="text-align: center;">
    <div style="width: 500px; margin: 0 auto; border-style: solid;">

    <h2>Transaction form</h2>

    <form action="/tx" method="POST">
    Sender:<br>
    <input type="text" name="sender" value="0xfee">
    <br>
    Receiver:<br>
    <input type="text" name="receiver" value="0xface"><br>
    Amount:<br>
    <input type="text" name="amount">
    <br><br>
    <input type="submit" value="Submit">
    </form> 
    </div>
    </div>
    </body>
    </html>
    """)


@app.route('/tx', methods=['POST'])
async def post_transaction(request):
    tx_data = {
        'sender': request.form.get('sender'),
        'receiver': request.form.get('receiver'),
        'amount': request.form.get('amount')
    }
    await handle_transaction(tx_data)
    return html('ok')
