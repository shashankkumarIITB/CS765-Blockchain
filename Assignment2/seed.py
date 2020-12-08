from datetime import datetime
import time

import config_seed as config
from miner import Miner
from threads import NodeThread
import helper

class Seed(Miner):
  def __init__(self, host, port, max_listen, withrandom=False, hashing_power=1, time_interarrival=1):
    # Call to the node constructor
    super().__init__(host, port, max_listen, 'seed', withrandom, hashing_power, time_interarrival)

  # Send the peer list to the connected peer
  def sendPeerList(self, addr, connection):
    peersFound = False
    string = 'Peers::'
    for peer in self.peers:
      if peer != addr:
        string += f'{peer},'
        peersFound = True
    if peersFound:
      string = string[:-1]
    return self.send(string, connection)

  # Function to send the existing blockchain
  def sendBlockchain(self, connection):
    self.lock_blockchain.acquire()
    blockFound = False
    string = 'Blockchain::'
    time_now = datetime.now().strftime('%Y-%m-%d %H%M%S')
    for block in self.blockchain[1:]:
      string += f'{time_now}:{block["host"]}:{block["port"]}:{block["block"].toString()},'
      blockFound = True
    if blockFound:
      string = string[:-1]
    self.lock_blockchain.release()
    self.send(string, connection)

  # Process dead node request
  def processDeadNode(self, request):
    timestamp, dead_host, dead_peer, sender_host, sender_peer = request.split(':')
    dead_peer = f'{dead_host}:{dead_peer}'
    if dead_peer in self.peers:
      self.peers.remove(dead_peer)

  # Function to parse request
  def parseRequest(self, request, connection=None):
    request_list = request.split('::')
    if request_list[0] == 'Connect':
      self.writeLog(request)
      peer = self.addPeer(request_list[1])
      self.sendPeerList(peer, connection)
    elif request_list[0] == 'Disconnect':
      self.writeLog(request)
      self.disconnectSeed(request_list[1])
      self.disconnectPeer(request_list[1])
    elif request_list[0] == 'Message':
      self.processMessage(request_list[1])
    elif request_list[0] == 'Blockchain':
      self.writeLog(request)
      self.sendBlockchain(connection)
    elif request_list[0] == 'Block':
      self.processBlock(request_list[1])
    elif request_list[0] == 'DeadNode':
      self.writeLog(request)
      self.processDeadNode(request_list[1])
    else:
      self.writeLog(f'Invalid:Unexpected request - {request}')

if __name__ == '__main__':
  # Create a seed instance
  seed = Seed(config.HOST, config.PORT, config.MAX_LISTEN, False)
  seed.writeLog(f'Seed::Accepting connections on {seed.host}:{seed.port}')

  # Create a thread to receive requests
  thread_recv = NodeThread(seed, 'recv')
  thread_pow = NodeThread(seed, 'pow')

  # Start the thread
  thread_recv.start()
  thread_pow.start()

