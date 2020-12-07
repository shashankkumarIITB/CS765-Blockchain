from seed import Seed
from peer import Peer
from threads import NodeThread
import config_peer, config_seed

if __name__ == '__main__':
	# Interarrival time of the network in seconds
	time_interarrival = 2

	# ######################## SEED ########################
	# Create a seed instance
	seed = Seed(config_seed.HOST, config_seed.PORT, config_seed.MAX_LISTEN, False)
	seed.writeLog(f'Seed::Accepting connections on {seed.host}:{seed.port}')

	# Create a thread to receive requests
	thread_recv = NodeThread(seed, 'recv')
	thread_pow = NodeThread(seed, 'pow')

	# Start the thread
	thread_recv.start()
	thread_pow.start()

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

	# ######################## ADVERSARY ########################
	# Create a peer instance behaving as adversary with port 5000
	port = 5000
	peer = Peer(config_peer.HOST, port, config_peer.MAX_LISTEN, withRandom=False, hashing_power=33, time_interarrival=time_interarrival)
	peer.connectToSeeds()
	peer.connectToPeers()

	# Flood node with port 4000
	flood_nodes = [f'{config_peer.HOST}:{config_peer.PORT}']

	# Create threads for the peer to send and receive messages
	thread_recv = NodeThread(peer, 'recv')
	thread_pow = NodeThread(peer, 'pow')
	thread_flood = NodeThread(peer, 'flood', flood_nodes)

	# Start the threads
	thread_recv.start()
	thread_pow.start()
	thread_flood.start()
