import csv, threading, socket
import config_peer as config
import helper
from node import Node

class Peer(Node):
  peers = set()
  num_seeds = 0
  seeds = []

  def __init__(self, host, port, max_listen):
    # Number of seeds to connect in the network
    self.num_seeds = config.NUM_SEEDS // 2 + 1
    # Call to the node constructor
    super().__init__(host, port, max_listen, True)

  # Get peer list from the connected seeds
  def getPeerList(self):    
    string = self.receive()
    for peer in string.split(','):
      self.peers.add(peer)

  # Connect to the seeds in the network
  def connectToSeeds(self):
    # Index of seeds to connect to in the network
    indices = helper.GetRandomList(1, config.NUM_SEEDS, self.num_seeds)
    
    print(f'Client: Connecting to server using {self.host}:{self.port}')

    # Read the seed attributes from the csv file
    with open('seeds.csv', 'r', newline='\n') as file:
      reader = csv.DictReader(file, delimiter=',')
      for i in range(self.num_seeds):
        row = next(reader)
        if i+1 in indices:
          # Create a socket instance for the peer
          peer = Peer(self.host, self.port, self.max_listen)
          # Register the peer node with the seed 
          peer.connect(row['host'], int(row['port']))
          connectionString = f'Connect:{self.host}:{self.port}'
          peer.send(connectionString)
          peer.getPeerList()
          print(peer.peers)

peer = Peer(config.HOST, config.PORT, config.MAX_LISTEN)
peer.connectToSeeds()