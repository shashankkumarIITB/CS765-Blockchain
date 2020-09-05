import config_seed as config
from node import Node

class Seed(Node):
  # Set to store the peers connected to this seed
  peers = set()

  # Function to parse request, returns whether to close the connection
  def parseRequest(self, request, connection):
    request_list = request.split('::')
    if (request_list[0] == 'Connect'):
      addr = f'{request_list[1]}'
      self.peers.add(addr)
      self.sendPeerList(connection, addr)
      return True
    elif (request_list[0] == 'Disconnect'):
      addr = f'{request_list[1]}'
      if addr in self.peers:
        self.peers.remove(addr)
      return True
    else:
      print(request)
      return False

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
  
# Create a node instance for the seed
seed = Seed(config.HOST, config.PORT, config.MAX_LISTEN, False)

# Bind and listen on the node
seed.bind()
seed.listen()

# Accept connections on the seed
print(f'Node: Accepting connections on {seed.host}:{seed.port}')
while True:
  conn = seed.accept()
  close = False
  while not close:
    request = seed.receive(conn)
    close = seed.parseRequest(request, conn)
  conn.close()
  seed.printPeerList()
