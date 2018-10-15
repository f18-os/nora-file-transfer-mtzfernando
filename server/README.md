# TCP Server (Threads)

This is the TCP server side of the lab using threads. This code allows for multiple clients to put a file on the
server (PUT). The server checks to see if the file already exists on the server. If not, it receives the file and
saves it. The multiple clients are handled by threads. The synchronization of the threads are handled by mutex Lock.
Every time a connection is made the server creates a new thread to take care of the request.

## Usage

python3 fileThreadServer.py

Options:
* -l or --listenPort The port to listen on				        `default: 50001`
* -d or --debug      To print debug statements in the code      `default: False`
* -? or --usage      Boolean to show how to run the program	    `default:False`
