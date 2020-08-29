import random, socket

class Node():
  s = None
  host, port = None, None
  max_listen = None
  greeting = "Welcome to the network!"
  MAX_BYTES = 10

  def __init__(self, host, port, max_listen, withrandom=False):
    # Create a socket instance
    # AF_INET => IPv4
    # SOCK_STREAM => TCP
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Configure the socket to reuse the port
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Set the host and port
    self.host = host
    self.port = int(port)
    if withrandom:
      self.port += random.randint(1, 100)
    self.max_listen = int(max_listen)

  # Bind the socket to a port
  def bind(self):
    self.s.bind((self.host, self.port))

  # Listen on the socket
  def listen(self):
    self.s.listen(self.max_listen)

  # Accept connections on the socket
  def accept(self):
    conn, addr = self.s.accept()
    print(f"Server: Received a request from {addr}")
    return conn 

  # Connect to the specified host and port
  def connect(self, host, port):
    self.s.connect((host, port))

  # Send the string after encoding it
  def send(self, string, connection=None):
    string = string.encode()
    chunks_sent = 0
    chunk_size = 0
    while chunks_sent < len(string):
      if connection:
        chunk_size = connection.send(string[chunks_sent : chunks_sent + self.MAX_BYTES])
      else:
        chunk_size = self.s.send(string[chunks_sent : chunks_sent + self.MAX_BYTES])
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
        chunk = self.s.recv(self.MAX_BYTES)
      string += chunk.decode()
      chunk_recv = len(chunk)
    return string

  # Close the socket connection
  def close(self):
    self.s.close()
