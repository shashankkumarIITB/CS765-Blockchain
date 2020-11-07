import random, socket, sys, threading
from datetime import datetime

import helper

# Format of messages stored:
# message = {
#   'timestamp': timestamp,
#   'host': host,
#   'port': port,
#   'hash': message_hash
#   }

class Node():
  MAX_BYTES = 10
  
  def __init__(self, host, port, max_listen, role, withrandom=False):
    # Lock to avoid race conditions while connecting to socket
    self.lock_socket = threading.Lock() 
    # Set the host and port
    self.host = host
    self.port = int(port)
    if withrandom:
      self.port += random.randint(1, 100)
    # Create two sockets - one as server and other as client
    # AF_INET => IPv4
    # SOCK_STREAM => TCP
    try:
      self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # Configure the socket to reuse the port
      self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as err:
      print(f'Error while creating socket on {host}:{port}')
      sys.exit(1)
    # Maximum number of connections to accept on the server socket
    self.max_listen = int(max_listen)
    # Hashes of the broadcasted messages
    self.hashes_message = set()
    # List of the messages broadcasted
    self.lock_messages = threading.Lock()
    self.messages = []
   
    # Set to store the connected nodes to this node with role as seed or peer
    self.role = role
    self.peers = set()
    self.seeds = set()

  # Bind the socket to a port
  def bind(self):
    try:
      self.server.bind((self.host, self.port))
    except socket.error as err:
      print(f'Error while binding {self.host}:{self.port}')

  # Listen on the socket
  def listen(self):
    try:
      self.server.listen(self.max_listen)
    except socket.error as err:
      print(f'Error while listening on {self.host}:{self.port}')

  # Accept connections on the socket
  def accept(self):
    try:
      conn, addr = self.server.accept()
      return conn 
    except socket.error as err:
      print(f'Error while accepting connection on {self.host}:{self.port} from {addr}')

  # Connect to the specified host and port and return True if connected
  def connect(self, host, port):
    try:
      self.lock_socket.acquire()
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.client.connect((host, int(port)))
      return True
    except socket.error as err:
      self.lock_socket.release()
      print(f'Error while connecting to {host}:{port}{err}')
      return False

  # Send the string after encoding it
  def send(self, string, connection=None):
    string = string.encode()
    chunks_sent = 0
    while chunks_sent < len(string):
      chunk_size = 0
      if connection:
        chunk_size = connection.send(string[chunks_sent : chunks_sent + self.MAX_BYTES])
      else:
        chunk_size = self.client.send(string[chunks_sent : chunks_sent + self.MAX_BYTES])
      chunks_sent += chunk_size

  # Receive the string 
  def receive(self, connection=None):
    string = ''
    chunk_recv = self.MAX_BYTES
    chunk = None
    while chunk_recv == self.MAX_BYTES:
      if connection:
        chunk = connection.recv(self.MAX_BYTES)
      else:
        chunk = self.client.recv(self.MAX_BYTES)
      string += chunk.decode()
      chunk_recv = len(chunk)
    return string

  # Close the socket connection
  def close(self):
    try:
      self.client.close()
    except socket.error as err:
      print(f'Error while closing socket on {host}:{port}')
    finally:
      self.lock_socket.release()

  # Function to add a peer
  def addPeer(self, request):
    timestamp, host, port = request.split(':')
    peer = f'{host}:{port}'
    self.peers.add(peer)
    return peer

  # Function to disconnect from a peer
  def disconnectPeer(self, request):
    timestamp, host, port = request.split(':')
    peer = f'{host}:{port}'
    if peer in self.peers:
      self.peers.remove(peer)

  # Function to disconnect from a seed
  def disconnectSeed(self, request):
    timestamp, host, port = request.split(':')
    peer = f'{host}:{port}'
    if seed in self.seeds:
      self.seeds.remove(seed)

  # Broadcast the hash of the message received
  def processMessage(self, request):
    timestamp, host, port, message = request.split(':')
    request_hash = helper.getHash(request)
    # Acquire the lock
    self.lock_messages.acquire()
    if request_hash not in self.hashes_message:
      message_hash = helper.getHash(message)
      message_dict = {
        'timestamp': timestamp,
        'host': host,
        'port': port,
        'hash': message_hash
      }
      # Add the hash of the message in the set of hashes 
      self.hashes_message.add(request_hash) 
      # Add message to the messages blockchain
      self.messages.append(message_dict)
      # Release the lock
      self.lock_messages.release()
      # Write to logfile
      self.writeLog(f'Message::{request}')
      # Broadcast to the nodes      
      self.broadcast(request, host, port)

  # Function to broadcast to the nodes
  def broadcast(self, request, host, port):
    # Broadcast to all the seeds except the sender
    sender = f'{host}:{port}'
    seeds = self.seeds.copy()
    for seed in seeds:
      if sender != seed:
        host, port = seed.split(':')
        self.connect(host, int(port))
        self.send(request)
        self.close()

    # Broadcast to all the peers except the sender if the node is a peer node
    if self.role == 'peer' or True:
      peers = self.peers.copy()
      for peer in peers:
        if sender != peer:
          host, port = peer.split(':')
          self.connect(host, int(port))
          self.send(request)
          self.close()

  # Function to write log to file
  def writeLog(self, string):
    with open(f'logfiles/logfile_{self.port}.txt', 'a+') as file:
      time_now = datetime.now().strftime('%Y-%m-%d %H%M%S')
      string = f'{time_now}::{string}'
      print(string)
      file.write(f'{string}\n')