import click
import socket
import threading
import os
import sys
import errno
import time
from pathlib import Path


CRLF = '\r\n'
path_to_dir = "./wwwroot"

@click.command()
@click.option("-v", is_flag=True, help="Prints debugging messages")
@click.option(
    "-p",
    type=int,
    name='PORT',
    default=8080,
    help="Specifies the port number that the server will listen and server at."
    "Default is 8080."
)
@click.option(
    "-d",
    type=str,
    name='PATH-TO-DIR',
    default="./wwwroot",
    help="Specifies the directory when launching the application."
    "Default is the current directory."
)
def httpfs(v, p, d):
    """
    httpfs is a simple file server.

    usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]
    """

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    invalid_path_vals = ["sudo", "su", "-i", "..", "rm", "-r", "-f"]

    if invalid_path_vals in d:
        path_to_dir = d.default
        print("Invalid path; using default: ./wwwroot")

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

        print("Data received from client ", clientAddress, ": ", data)

        # Check get/post
        request_line = data.splitlines()[0].split(" ")
        verb = request_line[0]
        path = Path(request_line[1])
        version = request_line[2]
        invalid_path_vals = ["sudo", "su", "-i", "..", "rm", "-r", "-f"]
        headers = ""

        if invalid_path_vals in path:
            clientSocket.sendall(version + " 401 Unauthorized" + CRLF)

        else:
            if verb is "GET":
                if not path.exists():
                    clientSocket.sendall(version + " 400 Bad Request" + CRLF)

                if path.is_file():
                    f = open(path.__str__(), "rb")

                    message_body = f.readall()
                    response_line = version + " 200 OK" + CRLF
                    headers += "Content-Length:" + os.path.getsize(path.__str__()) + CRLF

                    clientSocket.sendall(response_line + headers + message_body.decode('utf-8'))
                    f.close()


            elif verb is "POST":
                f = open(path.__str__(), "w+")
                f.write()

        # Get: look for it
        # Post: create
        # Validate the path




    finally:
        clientSocket.close()



if __name__ == '__main__':
    httpfs()
