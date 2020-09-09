import config_seed as config
from node import Node
from threads import NodeThread
import time
import helper

class Seed(Node):

  def __init__(self, host, port, max_listen, withrandom):
    # Call to the node constructor
    super().__init__(host, port, max_listen, 'seed', False)

  # Print the list of all the peers connected through this seed
  def printPeerList(self):
    print('Node: Displaying list of peers on this seed')
    for peer in self.peers:
      print(f"{peer}")

  # Send the peer list to the connected peer
  def sendPeerList(self, addr, connection):
    peersFound = False
    string = 'Peers::'
    for peer in self.peers:
      if peer != addr:
        string += f'{peer},'
        peersFound = True
    if peersFound:
      string = string[:-1]
    return self.send(string, connection)

  # Process dead node request
  def processDeadNode(self, request):
    timestamp, dead_host, dead_peer, sender_host, sender_peer = request.split(':')
    dead_peer = f'{dead_host}:{dead_peer}'
    if dead_peer in self.peers:
      self.peers.remove(dead_peer)

  # Function to parse request
  def parseRequest(self, request, connection=None):
    request_list = request.split('::')
    if request_list[0] == 'Connect':
      peer = self.addPeer(request_list[1])
      print(self.printPeerList())
      self.sendPeerList(peer, connection)
    elif request_list[0] == 'Disconnect':
      self.disconnectSeed(request_list[1])
      self.disconnectPeer(request_list[1])
    elif request_list[0] == 'Message':
      self.broadcastMessage(request_list[1])
    elif request_list[0] == 'DeadNode':
      self.processDeadNode(request_list[1])
    else:
      print(request)

# Create a seed instance
seed = Seed(config.HOST, config.PORT, config.MAX_LISTEN, False)
print(f'Node: Accepting connections on {seed.host}:{seed.port}')

# Create a thread to receive requests
thread_recv = NodeThread(seed, 'recv')

# Start the thread
thread_recv.start()

