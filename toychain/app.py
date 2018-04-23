import datetime as dt
import sys
import os
sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

import flask
from flask import jsonify, make_response, request

from block import Block
from node import append_block, get_chain, add_addr

app = flask.Flask(__name__)


@app.route('/toychain')
def index():
    msg = request.args.get('msg')
    if msg == '天王盖地虎':
        add_addr('http://{}:5001'.format(request.remote_addr))
        return ' 宝塔镇河妖'
    else:
        return 401


@app.route('/blocks', methods=['GET'])
def blocks():
    return make_response(jsonify([b.__dict__ for b in get_chain()]))


@app.route('/blocks', methods=['POST'])
def new_block():
    data = request.get_json()
    block = Block(
        data['index'], data['timestamp'], data['data'], data['prev_hash'], data['target'],
        nonce=data['nonce'])
    append_block(block)
    return make_response(jsonify([block.__dict__ for block in get_chain()]))


@app.route('/height', methods=['GET'])
def height():
    return make_response(jsonify(height=len(get_chain())))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
