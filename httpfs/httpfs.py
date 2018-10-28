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
    type=int,
    default=8080,
    help="Specifies the port number that the server will listen and server at."
    "Default is 8080."
)
@click.option(
    "-d",
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

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        serverSocket.bind(("127.0.0.1", p))
        serverSocket.listen(5)
        print("HTTP File Server listening on 127.0.0.1, port", str(p))

        while True:
            (clientSocket, address) = serverSocket.accept()
            threading.Thread(target=handleClientConnection, args=(clientSocket, address)).start()
    except OSError as e:
        print(e)
        sys.exit(1)
    finally:
        serverSocket.close()

def handleClientConnection(clientSocket, clientAddress):
    print("Connected to client: ", clientAddress)
    data = ""
    try:
        while True:
            buffer = clientSocket.recv(1024)
            if not buffer:
                break
            else:
                data += str(buffer.decode("utf-8"))

        print("data received: ", data)
    finally:
        clientSocket.close()



if __name__ == '__main__':
    httpfs()
