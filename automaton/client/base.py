import sys


class ClientInterface:

  def __init__(self, server='localhost', port=9090):
    self.client = None

  # Opens a connection to the server and registers the client
  def open(self):
    self.serviceid = None

  # Unregisters from the server then closes the connection
  def close(self):
    pass

  def getAvailableServices(self):
    return self.client.getAvailableServices()

  def isService(self, name):
    return self.client.isService(name)

  def allowService(self, name):
    return self.client.allowService(self.clientid, name)

  def disallowService(self, name):
    return self.client.disallowService(self.clientid, name)

  def allowAllServices(self):
    return self.client.allowAllServices(self.clientid)

  def disallowAllServices(self):
    return self.client.disallowAllServices(self.clientid)

  def execute(self, name, args):
    return self.client.execute(self.clientid, name, args)

  def interpret(self, raw):
    return self.client.interpret(self.clientid, raw)

  def serviceUsage(self, name):
    return self.client.serviceUsage(name)