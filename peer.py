import csv, threading, socket
import config_peer as config
import helper
from node import Node
from threads import NodeThread

class Peer(Node):
  def __init__(self, host, port, max_listen):
    # Number of seeds to connect in the network
    self.num_seeds = config.NUM_SEEDS // 2 + 1
    self.seeds = []
    self.peers = []
    self.peers_available = set()
    # Call to the node constructor
    super().__init__(host, port, max_listen, True)

  # Connect to the seeds in the network
  def connectToSeeds(self):
    # Index of seeds to connect to in the network
    indices = helper.GetRandomList(0, config.NUM_SEEDS - 1, self.num_seeds)    
    print(f'Node: Connecting to server using {self.host}:{self.port}')

    # Read the seed attributes from the csv file
    with open('seeds.csv', 'r', newline='\n') as file:
      reader = csv.DictReader(file, delimiter=',')
      string_connect = f'Connect::{self.host}:{self.port}'
      for i in range(self.num_seeds):
        row = next(reader)
        if i in indices:
          self.connect(row['host'], int(row['port']))
          self.send(string_connect)
          self.getPeerList()
          self.seeds.append(f'{row["host"]}:{row["port"]}')
          self.close()

  # Get peer list from the connected seeds
  def getPeerList(self):    
    string = self.receive()
    string = string.split('::')
    if string[0] == 'Peers':
      for peer in string[1].split(','):
        self.peers_available.add(peer)

  # Connect to peers on the network
  def connectToPeers(self):
    if len(self.peers_available) > 0:
      # Indices of peers to connect this peer
      indices = helper.GetRandomList(0, len(self.peers_available) - 1, config.NUM_PEERS)
      # Add the peers to the peers list
      peers_list = list(self.peers_available)
      for i in range(config.NUM_PEERS):
        self.peers.append(peers_list[indices[i]])

  # Function to parse request
  def parseRequest(self, request, connection):
    request_list = request.split('::')
    if (request_list[0] == 'Disconnect'):
      addr = f'{request_list[1]}'
      if addr in self.peers:
        self.peers.remove(addr)
    else:
      print(request)


# Create a peer instance 
peer = Peer(config.HOST, config.PORT, config.MAX_LISTEN)
peer.connectToSeeds()
peer.connectToPeers()

thread_recv = NodeThread(peer, 'recv')
thread_send = NodeThread(peer, 'send')

thread_recv.start()
thread_send.start()