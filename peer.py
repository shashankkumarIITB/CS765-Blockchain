import csv, threading, socket
import config_peer as config
import helper
from node import Node
from threads import NodeThread
from datetime import datetime

class Peer(Node):
  def __init__(self, host, port, max_listen):
    # Number of seeds to connect in the network
    self.num_seeds = config.NUM_SEEDS // 2 + 1
    self.peers_available = set()
    self.peers_live = {}
    # Call to the node constructor
    super().__init__(host, port, max_listen, 'peer', True)

  # Connect to the seeds in the network
  def connectToSeeds(self):
    # Index of seeds to connect to in the network
    indices = helper.getRandomList(0, config.NUM_SEEDS - 1, self.num_seeds)    
    print(f'Node: Connecting to server using {self.host}:{self.port}')

    # Read the seed attributes from the csv file
    with open('seeds.csv', 'r', newline='\n') as file:
      reader = csv.DictReader(file, delimiter=',')
      time_now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
      string_connect = f'Connect::{time_now}:{self.host}:{self.port}'
      for i in range(self.num_seeds):
        row = next(reader)
        if i in indices:
          if self.connect(row['host'], row['port']):
            self.seeds.add(f'{row["host"]}:{row["port"]}')
            self.send(string_connect)
            self.getPeerList()
            self.close()

  # Get peer list from the connected seeds
  def getPeerList(self):    
    string = self.receive()
    if string != 'Peers::':
      string = string.split('::')
      if string[0] == 'Peers':
        for peer in string[1].split(','):
          self.peers_available.add(peer)
      else:
        print(f'Error in the peer list received')

  # Connect to peers on the network
  def connectToPeers(self):
    if len(self.peers_available) > 0:
      # Indices of peers to connect this peer
      indices = helper.getRandomList(0, len(self.peers_available) - 1, config.NUM_PEERS)
      # Add the peers to the peers list
      peers_list = list(self.peers_available)
      for i in indices:
        peer = peers_list[i]
        self.peers.add(peer)
        self.peers_live[peer] = 0

  # Function to send liveness reply if a request is received
  def sendLivenessReply(self, request):
    timestamp, host, port = request.split(':')
    string = f'LivenessReply::{timestamp}:{host}:{port}:{self.host}:{self.port}'
    if self.connect(host, port):
      self.send(string)
      self.close()

  # Function to process the liveness reply received
  def processLivenessReply(self, request):
    timestamp, self_host, self_port, sender_host, sender_port = request.split(':')
    peer = f'{sender_host}:{sender_port}'
    if peer in self.peers:
      self.peers_live[peer] -= 1

  # Function to report a dead peer to the seed
  def reportDeadPeer(self, peer):
    self.peers.remove(peer)
    self.peers_live.pop(peer)
    time_now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    string = f'DeadNode::{time_now}:{peer}:{self.host}:{self.port}'
    for seed in self.seeds:
      host, port = seed.split(':')
      if self.connect(host, port):
        self.send(string)
        self.close()

  # Function to parse request
  def parseRequest(self, request, connection=None):
    print(request)
    request_list = request.split('::')
    if request_list[0] == 'Disconnect':
      self.disconnectSeed(request_list[1])
      self.disconnectPeer(request_list[1])
    elif request_list[0] == 'Message':
      self.broadcastMessage(request_list[1])
    elif request_list[0] == 'LivenessRequest':
      self.sendLivenessReply(request_list[1])
    elif request_list[0] == 'LivenessReply':
      self.processLivenessReply(request_list[1])
    else:
      print(request)

# Create a peer instance 
peer = Peer(config.HOST, config.PORT, config.MAX_LISTEN)
peer.connectToSeeds()
peer.connectToPeers()

# Create threads for the peer to send and receive messages
thread_recv = NodeThread(peer, 'recv')
thread_send = NodeThread(peer, 'send')
thread_live = NodeThread(peer, 'live')

# Start the threads
thread_recv.start()
thread_send.start()
thread_live.start()