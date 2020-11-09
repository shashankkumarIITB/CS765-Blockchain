from peer import Peer
from threads import NodeThread
import config_peer as config

if __name__ == '__main__':
	# Create a peer instance 
	peer = Peer(config.HOST, config.PORT, config.MAX_LISTEN, True, hashing_power=33)
	peer.connectToSeeds()
	peer.connectToPeers()

	# Create threads for the peer to send and receive messages
	thread_recv = NodeThread(peer, 'recv')
	thread_pow = NodeThread(peer, 'pow')

	# Start the threads
	thread_recv.start()
	thread_pow.start()
