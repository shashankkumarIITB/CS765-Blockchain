import threading, time
from datetime import datetime 
from block import Block

# Thread class to receive and send data  
class NodeThread(threading.Thread):
  def __init__(self, node, role, flood_nodes=None):
    threading.Thread.__init__(self)
    self.node = node
    self.role = role
    self.flood_nodes = flood_nodes

  def run(self, string=''):
    if self.role == 'recv':
      self.run_recv()
    elif self.role == 'send':
      self.run_message()
    elif self.role == 'live':
      self.run_live()
    elif self.role == 'pow':
      if self.node.role == 'peer':
        self.run_pow_peer()
      elif self.node.role == 'seed':
        self.run_pow_seed()
    elif self.role == 'flood':
      self.run_flood_network()

  def run_recv(self):
    # Bind and listen on the node
    self.node.bind()
    self.node.listen()
    # Accept the connections
    while True:
      conn = self.node.accept()
      request = self.node.receive(conn)
      self.node.parseRequest(request, conn)
      conn.close()

  def run_message(self):
    # Message to be sent
    for _ in range(10):
      time.sleep(5)
      # Create the message string
      time_now = datetime.now().strftime('%Y-%m-%d %H%M%S')
      string = f'Message::{time_now}:{self.node.host}:{self.node.port}:Hello World!'
      # Broadcast the message
      self.node.broadcast(string, self.node.host, self.node.port)
   
  def run_live(self):
    # Send liveliness messages to peers in the nodes
    while True:
      time.sleep(13)
      # Create the liveness message
      time_now = datetime.now().strftime('%Y-%m-%d %H%M%S')
      string = f'LivenessRequest::{time_now}:{self.node.host}:{self.node.port}'
      peers = self.node.peers.copy()
      # Send the message to the peers
      for peer in peers:
        requests_sent = self.node.peers_live[peer]
        if requests_sent < 3:
          host, port = peer.split(':')
          if self.node.connect(host, port):
            self.node.send(string)
            self.node.close()
          self.node.peers_live[peer] += 1
        else:
          self.node.reportDeadPeer(peer)

  # PoW implementation for the peer nodes
  def run_pow_peer(self):
    while True:
      # Time before the node generates the next block
      time_tosleep = int(self.node.computeWaitingTime())
      print(f'Time to sleep: {time_tosleep}')
      # Sleep until pending queue is empty
      while len(self.node.pending_blocks) == 0:
        if time_tosleep == 0:
          # Acquire lock for generating and inserting block
          self.node.lock_blockchain.acquire()
          # Create a new block
          block, length = self.node.generateBlock()
          # Insert the block
          self.node.insertBlock(block, length, self.node.host, self.node.port)
          # Release the blockchain lock
          self.node.lock_blockchain.release()
          # Create the block as string with the current timestamp
          time_now = datetime.now().strftime('%Y-%m-%d %H%M%S')
          string = f'Block::{time_now}:{self.node.host}:{self.node.port}:{block.toString()}' 
          self.node.broadcast(string, self.node.host, self.node.port)
          self.node.writeLog(f'Generated {string}')
          break
        time.sleep(1)
        time_tosleep -= 1
      # Validate the blocks
      self.node.validateBlocks()

  # Function for PoW for the seed nodes
  def run_pow_seed(self):
    while True:
      self.node.validateBlocks()

  # Function to flood the network with useless blocks
  def run_flood_network(self):
    # Invalid block to be sent
    block_invalid = Block(hash_prev='-1')
    while True:
      # Time before the node generates the fake block
      time_tosleep = 2
      # Sleep until timer expires
      while time_tosleep > 0:
        time.sleep(1)
        time_tosleep -= 1

        # Send the block to the selected nodes 
        for node in self.flood_nodes:
          host, port = node.split(':')
          if self.node.connect(host, port):
            time_now = datetime.now().strftime('%Y-%m-%d %H%M%S')
            string = f'Block::{time_now}:{self.node.host}:{self.node.port}:{block_invalid.toString()}' 
            self.node.send(string)
            self.node.close()
