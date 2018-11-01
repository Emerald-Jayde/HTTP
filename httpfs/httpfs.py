import click
import socket
import threading
import os
import sys

from pathlib import Path

CRLF = "\r\n"
path_to_dir = "./wwwroot"
invalid_path_vals = ["sudo", "su", "-i", "..", "rm", "-r", "-f"]

@click.command()
@click.option("-v", is_flag=True, help="Prints debugging messages")
@click.option(
    "-p",
    type=int,
    default=8080,
    help="Specifies the port number that the server will listen and server at."
    "Default is 8080.",
    show_default=True
)
@click.option(
    "-d",
    type=str,
    default="./wwwroot",
    help="Specifies the directory when launching the application."
    "Default is the current directory.",
    show_default=True
)
def httpfs(v, p, d):
    """
    httpfs is a simple file server.

usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]A'
    """
    global CRLF
    global path_to_dir
    global invalid_path_vals

    if d:
        path_to_dir = d

    tmp_root = Path(path_to_dir)
    if not tmp_root.is_dir():
        try:
            tmp_root.mkdir(parents=True, exist_ok=False)
        except FileExistsError as e:
            if v:
                print("Directory already exists.", end=CRLF)
                print(e)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind(("127.0.0.1", p))
        server_socket.listen(5)
        if v:
            print("HTTP File Server listening on 127.0.0.1, port", str(p), end=CRLF)

        while True:
            (client_socket, address) = server_socket.accept()
            # threading.Thread(
            #     target=handle_client_connection,
            #     args=(v, client_socket, address)
            # ).start()
            handle_client_connection(v, client_socket, address)
    except OSError as e:
        if v:
            print(e, end=CRLF)
            print("Server shutting down.")
        sys.exit(1)
    finally:
        server_socket.close()


def handle_client_connection(vflag, client_socket, client_address):
    global CRLF
    global path_to_dir
    global invalid_path_vals

    if vflag:
        print("Connected to client: ", client_address, end=CRLF)

    msg_rcvd = ""

    while True:
        buffer = client_socket.recv(1024)
        msg_rcvd += str(buffer.decode("utf-8"))
        if sys.getsizeof(buffer) < 1024:
            break

    if vflag:
        print(
            "Data received from client",
            client_address,
            ":\n",
            msg_rcvd,
            end=CRLF
        )

    # Splits client message by CRLF
    msg_rcvd_lines = msg_rcvd.splitlines()
    splitter = msg_rcvd_lines.index('')

    # HEADERS
    # Extract headers
    msg_rcvd_headers = msg_rcvd_lines[1:splitter]

    # BODY
    # Extract message body
    msg_rcvd_body = "\n".join(msg_rcvd_lines[splitter:])

    # REQUEST LINE
    # Extract request line
    msg_rcvd_request_line = msg_rcvd_lines[0].split(" ")
    # Extract HTTP verb
    verb = msg_rcvd_request_line[0]
    # Extract URL/path
    client_path = msg_rcvd_request_line[1]
    path = Path(path_to_dir + client_path)
    # Extract HTTP version
    protocol_version = msg_rcvd_request_line[2]

    invalid = any(
        invalid_path_val in path.__str__()
        for invalid_path_val in invalid_path_vals
    )

    if path.exists() and invalid:
        resp_line = protocol_version + "  401 Unauthorized" + CRLF
        headers = 2 * CRLF
        msg_body = CRLF
        msg_to_send = resp_line + headers + msg_body
        client_socket.sendall(msg_to_send.encode("utf-8"))
    else:
        if verb == 'GET':
            if not path.exists():
                resp_line = protocol_version + " 400 Bad Request" + CRLF
                headers = 2 * CRLF
                msg_body = CRLF
                msg_to_send = resp_line + headers + msg_body
                client_socket.sendall(msg_to_send.encode("utf-8"))

            if path.is_file():
                with open(path.__str__(), "rb") as file:
                    read_data = file.read()
                try:
                    resp_line = protocol_version + " 200 OK" + CRLF
                    headers = "Content-Length:" + \
                        str(os.path.getsize(path.__str__()) - 1) + CRLF + \
                        "Content-Type: text/html" +\
                         2 * CRLF
                    msg_body = read_data.decode("utf-8").lstrip()
                    msg_to_send = resp_line + headers + msg_body

                    client_socket.sendall(msg_to_send.encode("utf-8"))
                except OSError as e:
                    resp_line = protocol_version + \
                        " 500 Internal Server Error" + \
                        CRLF
                    headers = 2 * CRLF
                    msg_body = "File could not be opened/read from." + CRLF
                    msg_to_send = resp_line + headers + msg_body

                    client_socket.sendall(msg_to_send.encode("utf-8"))

                    if vflag:
                        print(e, end=CRLF)
            elif path.is_dir():
                dir_listing = os.listdir(path.__str__())
                if vflag:
                    print("Files in " + client_path + ":\n" + str(dir_listing))

                resp_line = protocol_version + " 200 OK" + CRLF
                headers = 2 * CRLF
                msg_body = "\n".join(dir_listing) + CRLF
                msg_to_send = resp_line + headers + msg_body

                client_socket.sendall(msg_to_send.encode("utf-8"))
        elif verb == 'POST':
            if not client_path or client_path is "/" or path.is_dir():
                resp_line = protocol_version + " 400 Bad Request" + CRLF
                headers = 2 * CRLF
                msg_body = "Cannot write to directory without file name." + CRLF
                msg_to_send = resp_line + headers + msg_body

                client_socket.sendall(msg_to_send.encode("utf-8"))
            else:
                if not path.exists():
                    parts_lst = path.parts
                    if len(parts_lst) > 2:
                        os.makedirs("/".join(parts_lst[:-1]))

                file = open(path.__str__(), "w+")
                try:
                    file.write(msg_rcvd_body)

                    resp_line = protocol_version + " 200 OK" + CRLF
                    headers = 2 * CRLF
                    msg_body = "Successfully wrote message:" + CRLF + \
                               msg_rcvd_body + 2 * CRLF + \
                               "To file: " + client_path + CRLF
                    msg_to_send = resp_line + headers + msg_body
                
                    client_socket.sendall(msg_to_send.encode("utf-8"))

                except OSError as e:
                    resp_line = protocol_version + \
                        " 500 Internal Server Error" + \
                        CRLF
                    headers = 2 * CRLF
                    msg_body = "File could not be opened/written to." + CRLF
                    msg_to_send = resp_line + headers + msg_body

                    client_socket.sendall(msg_to_send.encode("utf-8"))

                    if vflag:
                        print(e, end=CRLF)
                finally:
                    file.close()
        else:
            resp_line = protocol_version + \
                " 503 Service Unavailable" + \
                CRLF
            headers = 2 * CRLF
            msg_body = CRLF
            msg_to_send = resp_line + headers + msg_body

            client_socket.sendall(msg_to_send.encode("utf-8"))

        client_socket.close()


if __name__ == "__main__":
    httpfs()
