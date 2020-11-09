import time, threading
from numpy.random import Generator, PCG64

import config_peer as config
from node import Node
from block import Block
from threads import NodeThread

# Blockchain data:
# 1. length: Length of chain so far
# 2. block: block Bk-1
# 3. hash: Hash of the block Bk-1 

GENESIS_BLOCK = {
	'length': 1,
	'block': Block('0000', '0000'),
	'hash': '9e1c'
}

class Miner(Node):
	def __init__(self, host, port, max_listen, role, withRandom=True, hashing_power=1, time_interarrival=1):
		if role == 'peer':
			# Hashing power is in percentage
			self.hashing_power = hashing_power
			# Local lambda based on interarrival time
			self.lambda_ = self.hashing_power / time_interarrival / 100
			# Waiting time
			self.rg = Generator(PCG64())
		# Time allowed between blocks
		self.time_between = 3600
		# Blockchain to store blocks
		self.lock_blockchain = threading.Lock()
		self.block_hashes = set()
		self.blockchain = [GENESIS_BLOCK]
		# Queue to store pending blocks
		self.lock_pending = threading.Lock()
		self.pending_blocks = []
		
		# Call to the peer constructor
		super().__init__(host, port, max_listen, role, withRandom)

	def generateBlock(self, hash_prev):
		return Block(hash_prev)

	# Compute the waiting time based on the hashing power and block interarrival time
	def computeWaitingTime(self):
		return self.rg.exponential(scale=1 / self.lambda_)

	# Function to store and bradcast blocks of the blockchain
	def processBlock(self, request):
		timestamp_sent, host, port, hash_prev, merkle_root, timestamp_block = request.split(':')
		# Create a block from the request and add to the pending list
		data = {
			'block': Block(hash_prev, merkle_root, timestamp_block),
			'timestamp': timestamp_sent,
			'host': host,
			'port': port,
		}
		self.lock_pending.acquire()
		self.pending_blocks.append(data)
		self.lock_pending.release()
		# Write to logfile
		self.writeLog(f'Block::{request}')

	# Function to validate the blocks in the pending queue
	def validateBlocks(self):
		self.lock_pending.acquire()
		while len(self.pending_blocks) > 0:
			# Get the last block
			data = self.pending_blocks.pop(0)
			block, timestamp_sent, host, port = data['block'], data['timestamp'], data['host'], data['port']
			time_now = time.time()
			# Last block in the blockchain
			block_last = self.blockchain[-1]
			# Validate the block
			if (float(block.timestamp) < time_now + self.time_between and
				float(block.timestamp) > time_now - self.time_between and
				block.hash_prev == block_last['hash']):
				self.insertBlock(block)
				# Broadcast to the nodes
				self.broadcast(f'Block::{timestamp_sent}:{host}:{port}:{block.toString()}', host, port)
			else:
				self.writeLog('Miner::Discarded invalid block')
		self.lock_pending.release() 

	# Function to insert the block into blockchain
	def insertBlock(self, block):
		block_hash = block.getBlockHash()
		if block_hash not in self.block_hashes:
			# Create a block
			block_dict = {
				'length': len(self.blockchain) + 1,
				'block': block,
				'hash': block_hash
			}
			# Add the hash of the request in the set of hashes 
			self.block_hashes.add(block_hash) 
			# Add block to the blockchain
			self.blockchain.append(block_dict)
