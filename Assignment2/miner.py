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
# 4. host: User who generated the blockchain
# 5. port: Port number of the user

GENESIS_BLOCK = {
	'length': 1,
	'block': Block('0000', '0000'),
	'hash': '9e1c',
	'host': 'genesis',
	'port': '0000'
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
		self.block_hashes = set([GENESIS_BLOCK['hash']])
		self.blockchain = [GENESIS_BLOCK]
		# Queue to store pending blocks
		self.lock_pending = threading.Lock()
		self.pending_blocks = []
		
		# Call to the peer constructor
		super().__init__(host, port, max_listen, role, withRandom)

	# Function to generate a block after Proof-of-Work
	def generateBlock(self):
		# Acquire lock to the blockchain before calling this function
		# Find out the longest chain and store the hash
		length = 0
		hash_prev = None
		for block in self.blockchain:
			if block['length'] > length:
				length = block['length']
				hash_prev = block['hash']
		# Create a block
		return Block(hash_prev), length + 1

	# Compute the waiting time based on the hashing power and block interarrival time
	def computeWaitingTime(self):
		return self.rg.exponential(scale=1 / self.lambda_)

	# Function to store and bradcast blocks of the blockchain
	def processBlock(self, request):
		timestamp_sent, host_block, port_block, hash_prev, merkle_root, timestamp_block = request.split(':')
		# Create a block from the request and add to the pending list
		data = {
			'block': Block(hash_prev, merkle_root, timestamp_block),
			'host': host_block,
			'port': port_block
		}
		self.lock_pending.acquire()
		self.pending_blocks.append(data)
		self.lock_pending.release()
		# Write to logfile
		self.writeLog(f'Received::{request}')

	# Function to validate the blocks in the pending queue
	def validateBlocks(self):
		self.lock_pending.acquire()
		self.lock_blockchain.acquire()
		while len(self.pending_blocks) > 0:
			# Get the last block
			data = self.pending_blocks.pop(0)
			block, host_block, port_block = data['block'], data['host'], data['port']
			time_now = time.time()
			# Validate the block
			if (float(block.timestamp) < time_now + self.time_between and
				float(block.timestamp) > time_now - self.time_between and
				block.hash_prev in self.block_hashes):
				# Insert the block
				if (self.insertBlock(block, host_block, port_block)):
					# Broadcast to the nodes if the block was not present in the blockchain
					string = f'Block::{time_now}:{host_block}:{port_block}:{block.toString()}'
					self.broadcast(string, host_block, port_block)
					self.writeLog(string)
			else:
				self.writeLog('Miner::Discarded invalid block')
		self.lock_blockchain.release() 
		self.lock_pending.release() 

	# Function to find the length of the blockchain when a block with the given previous hash is inserted
	def getLength(self, hash_prev):
		# Acquire the lock to the blockchain before calling this function
		length = 0
		for block in self.blockchain:
			if block['hash'] == hash_prev:
				length = block['length'] + 1
				break
		return length

	# Function to insert the block into blockchain, returns true if the block is added to the blockchain
	def insertBlock(self, block, host, port, length=None):
		# Host and port are that of the creator of the block
		# The lock to the blockchain should be acquired before calling this function
		block_hash = block.getBlockHash()
		# Check if the block exists in the blockchain
		if block_hash not in self.block_hashes: 
			if not length:
				length = self.getLength(block.hash_prev)
			# Create a block
			block_dict = {
				'length': length,
				'block': block,
				'hash': block_hash,
				'host': host,
				'port': port
			}
			# Add the hash of the request in the set of hashes 
			self.block_hashes.add(block_hash) 
			# Add block to the blockchain
			self.blockchain.append(block_dict)
			# Write the block to the database
			self.writeDatabase(block_dict)
			return True
		return False

