import click
import socket
import threading
import os
import sys
import errno
import time


@click.command()
@click.option("-v", is_flag=True, help="Prints debugging messages")
@click.option(
    "-p",
    is_flag=True,
    type=int,
    default=8080,
    help="Specifies the port number that the server will listen and server at."
    "Default is 8080."
)
@click.option(
    "-d",
    is_flag=True,
    type=str,
    default="./",
    help="Specifies the directory when launching the application."
    "Default is the current directory."
)
def httpfs(v, p, d):
    """
    httpfs is a simple file server.

    usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]
    """

    data = ""
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setblocking(False)
    serverSocket.bind((socket.gethostname(), p))
    serverSocket.listen(1)

    while True:
        try:
            (clientSocket, address) = serverSocket.accept()
            print("Connected to: %s", address)

            while True:
                buffer = clientSocket.recv(1024)
                if not data:
                    break
                else:
                    data += "%s%s" % (data, buffer)
                    
            print("data received: %s", data)
        except BlockingIOError as e:
            if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                print("No data available")
                time.sleep(3)
            else:
                # a "real" error occurred
                print(e)
                sys.exit(1)

    clientSocket.close()
    serverSocket.close()

if __name__ == '__main__':
    httpfs()
