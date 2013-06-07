###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS


class EchoServerProtocol(WebSocketServerProtocol):

   def onConnect(self, connectionRequest):
      print "WebSocket extensions in use: %s" % connectionRequest.extensions

   def onOpen(self):
      pass

   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WebSocketServerFactory("ws://localhost:9000",
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoServerProtocol

#   factory.setProtocolOptions(autoFragmentSize = 4)

   ## Enable WebSocket extension "permessage-deflate". This is all you
   ## need to do (unless you know what you are doing .. see below)!
   ##
   factory.setProtocolOptions(perMessageDeflate = True)

   ## accept any configuration, request no specific features: this is the default!
   def accept1(acceptNoContextTakeover, acceptMaxWindowBits, requestNoContextTakeover, requestMaxWindowBits):
      return (False, 0)

   ## accept if client offer signals support for "no context takeover" and "max window size". if so, 
   ## request "no context takeover" and "max window size" of 2^8. else decline offer.
   def accept2(acceptNoContextTakeover, acceptMaxWindowBits, requestNoContextTakeover, requestMaxWindowBits):
      if acceptNoContextTakeover and acceptMaxWindowBits:
         return (True, 8)
      else:
         return None

   ## deny offer if client requested to limit sliding window size, else accept,
   ## requesting no specific features.
   def accept3(acceptNoContextTakeover, acceptMaxWindowBits, requestNoContextTakeover, requestMaxWindowBits):
      if requestMaxWindowBits != 0:
         return None
      else:
         return (False, 0)

#   factory.setProtocolOptions(perMessageDeflateAccept = accept1)
   factory.setProtocolOptions(perMessageDeflateAccept = accept2)
#   factory.setProtocolOptions(perMessageDeflateAccept = accept3)

   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()