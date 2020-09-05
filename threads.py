import threading

# Thread class to receive and send messages 
class NodeThread(threading.Thread):
  def __init__(self, node, role):
    threading.Thread.__init__(self)
    self.node = node
    self.role = role

  def run(self, string=''):
    if self.role == 'recv':
      while True:
        # Accept the connections
        conn = self.node.accept()
        close = False
        # Check if the connection is to be closes
        while not close:
          request = self.node.receive(conn)
          close = self.node.parseRequest(request)
        conn.close()
    elif self.role == 'send':
      # Message to be sent
      string = 'Message::Hello World'
      for seed in self.node.seeds:
        string_disconnect = f'Disconnect::{seed}'
        host, port = seed.split(':')
        # Check if the socket is still connected
        data = self.node.receive()
        if data == None:
          self.node.connect(host, int(port))
        self.node.send(string)
        self.node.send(string_disconnect)