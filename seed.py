import config_seed as config
from node import Node

class Seed(Node):
  # Set to store the peers connected to this seed
  peers = set()

  # Function to parse request
  def parseRequest(self, request, connection):
    request = request.split(':')
    if (request[0] == 'Connect'):
      addr = f'{request[1]}:{request[2]}'
      self.peers.add(addr)
      self.sendPeerList(connection, addr)

  # Print the list of all the peers connected through this seed
  def printPeerList(self):
    print('Server: Displaying list of peers on this seed')
    for peer in self.peers:
      print(f"{peer}")

  # Send the peer list to the connected peer
  def sendPeerList(self, connection, addr):
    string = ''
    for peer in self.peers:
      if peer != addr:
        string += f'{peer},'
    return self.send(string[:-1], connection)
  
# Create a node instance for the seed
seed = Seed(config.HOST, config.PORT, config.MAX_LISTEN, True)

# Bind and listen on the node
seed.bind()
seed.listen()

# Accept connections on the seed
print(f'Server: Accepting connections on {seed.host}:{seed.port}')
while True:
  conn = seed.accept()
  request = seed.receive(conn)
  seed.parseRequest(request, conn)
  conn.close()
