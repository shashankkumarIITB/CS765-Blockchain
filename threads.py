import threading

# Thread class to receive and send messages 
class NodeThread(threading.Thread):
  def __init__(self, node, role):
    threading.Thread.__init__(self)
    self.node = node
    self.role = role

  def run(self, string=''):
    if self.role == 'recv':
      # Bind and listen on the node
      self.node.bind()
      self.node.listen()
      # Accept the connections
      while True:
        conn = self.node.accept()
        request = self.node.receive(conn)
        self.node.parseRequest(request, conn)
        conn.close()

    elif self.role == 'send':
      print('Entering sender role')
      # Message to be sent
      string = 'Message::Hello World'
      for seed in self.node.seeds:
        host, port = seed.split(':')
        self.node.connect(host, int(port))
        self.node.send(string)
        self.node.close()
