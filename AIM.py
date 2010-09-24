#!/usr/bin/env python

import sys
import os
sys.path.append('/home/dan/prg/Automaton/gen-py')
from twisted.words.protocols import oscar
from twisted.internet import protocol, reactor
import Automaton.lib.settings_loader as settings_loader

import Automaton.lib.logger as logger

import Automaton.lib.ClientWrapper as ClientWrapper

## unescape
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
# Provided by Fredrik Lundh at http://effbot.org/zone/re-sub.htm#unescape-html
import re, htmlentitydefs

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


op = {'HOST':'login.oscar.aol.com',
      'PORT':'5190',
      'USER':'',
      'PASS':''
     }

op.update(settings_loader.load_app_settings(sys.argv[0]))

# Fail if authentication info is not present.
for operator in ('USER', 'PASS', 'MASTER'):
  if op[operator] == '':
    logger.log("Missing necessary credentials to log in to AIM.")
    sys.exit()

class B(oscar.BOSConnection):
    capabilities = [oscar.CAP_CHAT]

    def __init__(self, s, p, **kwargs):
      self.client = ClientWrapper.ClientWrapper("tails.local")
      self.client.open()
      oscar.BOSConnection.__init__(self, s, p, **kwargs)

    def initDone(self):
        self.requestSelfInfo().addCallback(self.gotSelfInfo)
        self.requestSSI().addCallback(self.gotBuddyList)
    def gotSelfInfo(self, user):
        self.name = user.name
    def gotBuddyList(self, l):
        self.activateSSI()
        self.setIdleTime(0)
        self.clientReady()
        logger.log("Client online.")
    def receiveMessage(self, user, multiparts, flags):
        if user.name.upper() != op['MASTER'].upper():
          multiparts[0] = ("I don't take orders from you!",)
          self.lastUser = user.name
          self.sendMessage(user.name, multiparts)
        else:
          body = multiparts[0][0].strip()
          ix=body.find(' ')
          returned = ''
          args=''
          if ix > -1:
            args = unescape(body[ix+1:])
            body = unescape(body[0:ix])

          if self.client.isScript(body):
            self.client.registerScript(body)
            returned = self.client.execute(body, args)
          else:
            returned = "Command not found.\nDid you forget to import it?"

          multiparts[0] = (returned,)
          self.lastUser = user.name
          self.sendMessage(user.name, multiparts)

class OA(oscar.OscarAuthenticator):
   BOSClass = B

protocol.ClientCreator(reactor, OA, op['USER'], op['PASS']).connectTCP(op['HOST'], int(op['PORT']))
reactor.run()

