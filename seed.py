import config_seed as config
from node import Node
from threads import NodeThread

class Seed(Node):
  # Set to store the peers connected to this seed
  peers = set()

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
  
  # Function to parse request
  def parseRequest(self, request, connection):
    request_list = request.split('::')
    if (request_list[0] == 'Connect'):
      addr = f'{request_list[1]}'
      self.peers.add(addr)
      self.sendPeerList(connection, addr)
    elif (request_list[0] == 'Disconnect'):
      addr = f'{request_list[1]}'
      if addr in self.peers:
        self.peers.remove(addr)
    else:
      print(request)

# Create a seed instance
seed = Seed(config.HOST, config.PORT, config.MAX_LISTEN, False)
print(f'Node: Accepting connections on {seed.host}:{seed.port}')

# Start a thread to receive requests
thread_recv = NodeThread(seed, 'recv')

thread_recv.start()