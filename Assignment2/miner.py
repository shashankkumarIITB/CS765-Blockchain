import time, threading
from numpy.random import Generator, PCG64
# from peer import Peer
from block import Block

class Miner():
	def __init__(self, hashing_power=1, time_interarrival=1):
		# Hashing power is in percentage
		self.hashing_power = hashing_power
		# Local lambda based on interarrival time
		self.lambda_ = self.hashing_power / time_interarrival / 100
		# Generated block
		self.block = None
		# Waiting time
		self.rg = Generator(PCG64())
		self.waiting_time = None
		# Queue to store pending blocks
		self.lock = threading.Lock()
		self.counter = 0
		self.pending_blocks = []

	def generateBlock(self, hash_prev):
		self.block = Block(hash_prev)

	def computeWaitingTime(self):
		self.waiting_time = self.rg.exponential(scale=1 / self.lambda_)

	def validateBlocks(self):
		self.lock.acquire()
		while self.counter > 0:
			block = self.pending_blocks.pop(self.counter - 1)
			time_now = time.time()
			hash_prev = block.hash_prev
			

m = Miner()
m.computeWaitingTime()