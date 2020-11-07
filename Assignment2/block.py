import os, secrets, time

import helper

# Implementation of block in a blockchain
class Block():
	def __init__(self, hash_prev, merkle_root=None, timestamp=None):
		self.hash_prev = hash_prev
		self.merkle_root = merkle_root
		self.timestamp = timestamp
		if merkle_root == None:
			self.merkle_root = self.getMerkleRoot()
		if self.timestamp == None:
			self.timestamp = time.time()

	def getMerkleRoot(self, length=4):
		return secrets.token_hex(15)[:length]

	def getBlockHash(self, length=4):
		string = self.toString()
		return helper.getHash(string)[-length:]

	def toString(self):
		return f'{self.hash_prev}:{self.merkle_root}:{self.timestamp}'
