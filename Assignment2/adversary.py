from peer import Peer
from threads import NodeThread
import config_peer as config

if __name__ == '__main__':
	# Interarrival time of the network in seconds
	time_interarrival = 2
	
	# Create a peer instance behaving as adversary with port 5000
	port = 5000
	peer = Peer(config.HOST, port, config.MAX_LISTEN, withRandom=False, hashing_power=33, time_interarrival=time_interarrival)
	peer.connectToSeeds()
	peer.connectToPeers()

	# Nodes to flood
	flood_nodes = [f'{config.HOST}:{config.PORT}']

	# Create threads for the peer to send and receive messages
	thread_recv = NodeThread(peer, 'recv')
	thread_pow = NodeThread(peer, 'pow')
	thread_flood = NodeThread(peer, 'flood', flood_nodes)

	# Start the threads
	thread_recv.start()
	thread_pow.start()
	thread_flood.start()
