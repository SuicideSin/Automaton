import socket
import lib.settings_loader as settings_loader

class pandora:

  def execute(self, arg = ''):
    cmd_op = {"ip":"localhost", "port":"9900"}
    cmd_op.update(settings_loader.load_script_settings(__name__))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((cmd_op["ip"], int(cmd_op["port"])))
    sock.send(arg)
    response = sock.recv(1024)
    sock.close()
    return response

  def grammar(self):
    return  "pandora{"+\
              "keywords = pandora"+\
              "arguments = *"+\
            "}"

  def help(self):
    return """
            USAGE: pandora command
            Connects to the local Pandora client and sends a command to it
           """