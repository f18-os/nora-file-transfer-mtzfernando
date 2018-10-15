#! /usr/bin/env python3
import asyncio
import sys, os, socket, time
import threading
sys.path.append("../emphaticDemo")       # for params
import params
from threading import Thread
from framedSock import FramedStreamSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    lock = threading.Lock()     # Shared lock to synchronize threads
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        ServerThread.lock.acquire()                                         # Try to get the lock
        try:
            while True:
                msg = self.fsock.receivemsg()                               # Receive client request
                if not msg:
                    if self.debug: print(self.fsock, "server thread done")
                    return
                requestNum = ServerThread.requestCount
                time.sleep(0.001)
                ServerThread.requestCount = requestNum + 1

                if debug: print("rec'd: ", msg)

                if os.path.exists(msg):                                     # Check if the file is in the server already.
                    if debug: print("FILE ALREADY EXISTS")
                    self.fsock.sendmsg(b"File exists")                      # Send the file exists.
                    return
                else:
                    self.fsock.sendmsg(b"Ready")                            # Send the server is ready to receive the file.
                    with open(msg, 'w') as file:                            # Open file to receive
                        if debug: print("OPENED FILE")
                        while True:
                            msg = self.fsock.receivemsg()                   # Receive the file.
                            if debug: print("RECEIVED PAYLOAD: %s" % msg)
                            if not msg:                                     # Check if done receiving file.
                                if debug: print("DONE WRITING INSIDE NOT MSG")
                                return
                            else:
                                file.write(msg.decode())                    # Write the data to the file.
                                if debug: print("WROTE THE PAYLOAD TO FILE")
        finally:
            ServerThread.lock.release()                                     # Release the lock for the next thread.

while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
