#! /usr/bin/env python3

# Echo client program
import socket, sys, re
sys.path.append("../emphaticDemo")       # for params
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    (('-f', '--file'), "file", "constitution.txt")
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug, file_name = paramMap["server"], paramMap["usage"], paramMap["debug"], paramMap["file"]

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

       try:                                                                 # Try to open the file to put on server.
           file = open(file_name, 'r')                                      # Open the file.
           if debug: print("OPENED FILE")
           data = file.read(100)                                            # Read 100 bytes from the file.
       except IOError:
           print("File does not exists or unable to open. Shutting down!")  # Shutdown if unable to open file.
           sys.exit(0)

       fs = FramedStreamSock(s, debug=debug)

       fs.sendmsg(file_name.encode())                                       # Send the file request.
       response = fs.receivemsg()                                           # Wait for response.

       if response.decode() == "File exists":                               # If file already on the server shutdown.
           print("The file is already in the server. Closing the thread.")
           file.close()                                                     # Close the file.
           return
       else:                                                                # Finish sending the rest of the file 100 bytes at the time.
           print("Sending the file to the server!")
           while data:
               fs.sendmsg(data.encode())                                    # Send the data in the file, 100 bytes at a time.
               data = file.read(100)                                        # Read the next 100 bytes.
           file.close()                                                     # Close the file when done reading.
           fs.sendmsg(b"")                                                  # Send empty string to tell server client is done sending the file.

for i in range(10):
    ClientThread(serverHost, serverPort, debug)
