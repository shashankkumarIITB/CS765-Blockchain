import threading
import time
from datetime import datetime 

# Thread class to receive and send data  
class NodeThread(threading.Thread):
  def __init__(self, node, role):
    threading.Thread.__init__(self)
    self.node = node
    self.role = role

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
          # Acquire the lock
          self.node.lock_blockchain.acquire()
          last_hash = self.node.blockchain[-1]['hash'] 
          # Create a new block
          block = self.node.generateBlock(last_hash)
          self.node.insertBlock(block)
          print(f'Generated block: {block.toString()}')
          # Release the lock
          self.node.lock_blockchain.release()
          # Create the block as string
          time_now = datetime.now().strftime('%Y-%m-%d %H%M%S')
          string = f'Block::{time_now}:{self.node.host}:{self.node.port}:{block.toString()}' 
          self.node.broadcast(string, self.node.host, self.node.port)
          break
        time.sleep(1)
        time_tosleep -= 1
      # Validate the blocks
      self.node.validateBlocks()

  # Function for PoW for the seed nodes
  def run_pow_seed(self):
    while True:
      while len(self.node.pending_blocks) > 0:
        self.node.validateBlocks()

    