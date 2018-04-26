import time                                         #从系统导入time包，后面用到time包的time的方法
from hashlib import sha256
from threading import Thread

from block import Block                              #从block文件中导入Block类
from consensus import get_target             # 从consensus中导入 get_target类
from node import append_block, get_chain, find_neighbour, sync_chain


def proof_of_work(prev_block, new_block):   #定义方法，里面有两个参数
	base = '{}{}'.format(prev_block, new_block)                              #？？？

	nonce = 0      #从nonce为0开始运算
	target = get_target(get_chain())
	while True:
		h = sha256()
		h.update('{}{}'.format(base, nonce).encode('utf8'))    #h升级后，前面是base，后面是0，都用utf8编码
		res = int(h.hexdigest(), 16)                           #？？？
		print(res)                                             #打印res
		if res < target:                                       #res小于target
			print('solution found! {} @ target: {}'.format(nonce, hex(target)))
			return nonce
		time.sleep(1)  # 1h/s                         #程序在这暂停1s
		nonce += 1                                    # ？？？
        #The "nonce" in a bitcoin block is a 32-bit (4-byte) field whose value is set so that the hash of the block will contain a run of leading zeros.
        # nonce+1 添加一个新的nonce，进行行的hash运算。不停的递增nonce值，对得到的新字符串进行SHA256哈希运算，直到实现目标
def mine():
	prev_block = get_chain()[-1]  #读取列表中倒数第一个元素，倒数第一个为算出的符合的值
	block = Block(prev_block.index + 1, time.time(), 'mining test', prev_block.hash)
	solution = proof_of_work(prev_block, block)   #？？？
	block.nonce = solution        #？？？
	append_block(block)           #在列表末尾添加新元素


def main():                        #定义一个main方法
	# neighbour_worker = Thread(target=find_neighbour, daemon=False)
	sync_workder = Thread(target=sync_chain, daemon=False)       #？？？   线程开始之前设置daemon
	# neighbour_worker.start()
	sync_workder.start()    #线程开始
	while True:             #True哪来的？？？
		mine()

if __name__ == '__main__':   # 单独运行脚本使用的语句
	main()

# 增加难度值的参考  http://www.infoq.com/cn/articles/bitcoin-and-block-chain-part02
