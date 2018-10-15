#! /usr/bin/env python3

# Echo client program
import socket, sys, re
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    (('-f', '--file'), "file", "constitution.txt")
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug, file_name  = paramMap["server"], paramMap["usage"], paramMap["debug"], paramMap["file"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
       s = None
       for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
           af, socktype, proto, canonname, sa = res
           try:
               print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
               s = socket.socket(af, socktype, proto)
           except socket.error as msg:
               print(" error: %s" % msg)
               s = None
               continue
           try:
               print(" attempting to connect to %s" % repr(sa))
               s.connect(sa)
           except socket.error as msg:
               print(" error: %s" % msg)
               s.close()
               s = None
               continue
           break

       if s is None:
           print('could not open socket')
           sys.exit(1)

       framedSend(s, file_name.encode(), debug)  # Send the request for the file.
       response = framedReceive(s, debug)  # Wait for the response from the server.
       if response.decode() == "File exists":  # If file already on the server shutdown.
           print("The file is already in the server. Closing the socket")
           s.close()
       else:
           while data:  # Finish sending the rest of the file 100 bytes at the time.
               framedSend(s, data.encode(), debug)
               data = file.read(100)
           s.shutdown(socket.SHUT_WR)  # Shutdown the socket.

for i in range(100):
    ClientThread(serverHost, serverPort, debug)

