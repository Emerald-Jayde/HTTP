import click
import socket
import threading
import os
import sys
import errno
import time
from pathlib import Path

CRLF = "\r\n"
path_to_dir = "./wwwroot"


@click.command()
@click.option("-v", is_flag=True, help="Prints debugging messages")
@click.option(
    "-p",
    type=int,
    name="PORT",
    default=8080,
    help="Specifies the port number that the server will listen and server at."
    "Default is 8080."
)
@click.option(
    "-d",
    type=str,
    name="PATH-TO-DIR",
    default="./wwwroot",
    help="Specifies the directory when launching the application."
    "Default is the current directory."
)
def httpfs(v, p, d):
    """
    httpfs is a simple file server.

    usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]
    """

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    invalid_path_vals = ["sudo", "su", "-i", "..", "rm", "-r", "-f"]

    if invalid_path_vals in d:
        nonlocal path_to_dir = d.default
        print("Invalid path; using default: ./wwwroot")

    try:
        server_socket.bind(("127.0.0.1", p))
        server_socket.listen(5)
        print("HTTP File Server listening on 127.0.0.1, port", str(p))

        while True:
            (client_socket, address) = server_socket.accept()
            threading.Thread(target=handle_client_connection,
                             args=(client_socket, address)).start()
    except OSError as e:
        print(e)
        sys.exit(1)
    finally:
        server_socket.close()


def handle_client_connection(client_socket, client_address):
    print("Connected to client: ", client_address, end="\n")

    msg_rcvd = ""
    raw_msg_rcvd = ""

    while True:
        buffer = client_socket.recv(1024)
        if not buffer:
            break
        else:
            msg_rcvd += str(buffer.decode("utf-8"))
            raw_msg_rcvd += buffer

    print(
        "Data received from client ",
        client_address,
        ":",
        nonlocal CRLF,
        msg_rcvd,
        end="\n"
    )

    # Splits client message by CRLF
    msg_rcvd_lines = msg_rcvd.splitlines()

    # Extract request line
    msg_rcvd_request_line = msg_rcvd_lines()[0].split(" ")
    # Extract HTTP verb
    verb = request_line[0]
    # Extract URL/path
    path = Path(request_line[1])
    # Extract HTTP version
    protocol_version = request_line[2]

    # Extract headers
    msg_rcvd_headers = [
         header for header in msg_rcvd_lines[1:] if(":" in header)
    ]

     # Extract message body
     msg_rcvd_body = "\n".join(
        [
            msg_body_line
            for msg_body_line in msg_rcvd_lines[1:]
                if(":" not in header)
        ]
    )

      invalid_path_vals = ["sudo", "su", "-i", "..", "rm", "-r", "-f"]

       if invalid_path_vals in path:
            client_socket.sendall(
                protocol_version +
                " 401 Unauthorized" +
                3 * nonlocal CRLF
            )
        else:
            if verb is "GET":
                if not path.exists():
                    client_socket.sendall(
                        protocol_version +
                        " 400 Bad Request"+
                        3 * nonlocal CRLF
                    )
                if path.is_file():
                    try:
                        file = open(nonlocal path_to_dir + path.__str__(), "rb")

                        resp_line = protocol_version + " 200 OK" + nonlocal CRLF
                        headers = "Content-Length:" +
                            os.path.getsize(path.__str__()) +
                            nonlocal CRLF
                        msg_body = file.readall() + CRLF
                        client_socket.sendall(resp_line + headers + msg_body)

                        print("", end="\n")
                    except OSError as e:
                        resp_line = protocol_version +
                            " 500 Internal Server Error" +
                            nonlocal CRLF
                        headers = nonlocal CRLF
                        msg_body = "File could not be opened/read from." +
                            nonlocal CRLF
                        client_socket.sendall(resp_line + headers + msg_body)

                        print(e, end="\n")
                    finally:
                        file.close()
            elif verb is "POST":
                try:
                    file = open(nonlocal path_to_dir + path.__str__(), "w+")
                    file.write()

                    resp_line = protocol_version + " 200 OK" + nonlocal CRLF
                    headers = nonlocal CRLF
                    msg_body = nonlocal CRLF
                    client_socket.sendall(resp_line + headers + msg_body)
                except OSError as e:
                    resp_line = protocol_version +
                        " 500 Internal Server Error" +
                        nonlocal CRLF
                    headers = nonlocal CRLF
                    msg_body = "File could not be opened/written to." +
                        nonlocal CRLF
                    client_socket.sendall(resp_line + headers + msg_body)

                    print(e, end="\n")
                finally:
                    file.close()
            else:
                resp_line = protocol_version +
                    " 503 Service Unavilable" +
                    nonlocal CRLF
                headers = nonlocal CRLF
                msg_body = nonlocal CRLF
                client_socket.sendall(resp_line + headers + msg_body)

        client_socket.close()


if __name__ == "__main__":
    httpfs()
