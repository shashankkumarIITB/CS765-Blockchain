import time
from seed import Seed
from peer import Peer
from threads import NodeThread
import config_peer, config_seed

if __name__ == '__main__':
	# Interarrival time of the network in seconds
	time_interarrival = 2

	# ######################## PEERS ########################
	# Create a network of N honest nodes
	# Hashing power available to each node = (100 - hashing power with adversary) / N
	N = 10
	hashing_power_node =  (100 - 33) / N
	for i in range(N):
		peer = Peer(config_peer.HOST, config_peer.PORT + i, config_peer.MAX_LISTEN, withRandom=False, hashing_power=hashing_power_node, time_interarrival=time_interarrival)
		peer.connectToSeeds()
		peer.connectToPeers()

		# Create threads for the peer to send and receive messages
		thread_recv = NodeThread(peer, 'recv')
		thread_pow = NodeThread(peer, 'pow')

		# Start the threads
		thread_recv.start()
		thread_pow.start()
