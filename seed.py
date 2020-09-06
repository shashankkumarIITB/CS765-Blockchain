import config_seed as config
from node import Node
from threads import NodeThread
import time
import helper

class Seed(Node):

  def __init__(self, host, port, max_listen, withrandom):
  # Set to store the peers connected to this seed
    self.peers = set()
    self.seeds = set()
    # Call to the node constructor
    super().__init__(host, port, max_listen, False)

  # Print the list of all the peers connected through this seed
  def printPeerList(self):
    print('Node: Displaying list of peers on this seed')
    for peer in self.peers:
      print(f"{peer}")

  # Send the peer list to the connected peer
  def sendPeerList(self, connection, addr):
    string = 'Peers::'
    for peer in self.peers:
      if peer != addr:
        string += f'{peer},'
    return self.send(string[:-1], connection)

  # Process dead node request
  def processDeadNode(self, request):
    timestamp, dead_host, dead_peer, sender_host, sender_peer = request.split(':')
    dead_peer = f'{dead_host}:{dead_peer}'
    if dead_peer in self.peers:
      self.peers.remove(dead_peer)

  # Function to parse request
  def parseRequest(self, request, connection):
    request_list = request.split('::')
    if request_list[0] == 'Connect':
      addr = f'{request_list[1]}'
      self.peers.add(addr)
      self.sendPeerList(connection, addr)
    elif request_list[0] == 'Disconnect':
      addr = f'{request_list[1]}'
      if addr in self.peers:
        self.peers.remove(addr)
    elif request_list[0] == 'Message':
      self.broadcastMessage(request_list[1], )
    elif request_list[0] == 'DeadNode':
      self.processDeadNode(request_list[1])
    else:
      print(request)

# Create a seed instance
seed = Seed(config.HOST, config.PORT, config.MAX_LISTEN, False)
print(f'Node: Accepting connections on {seed.host}:{seed.port}')

# Start a thread to receive requests
thread_recv = NodeThread(seed, 'recv')

thread_recv.start()

