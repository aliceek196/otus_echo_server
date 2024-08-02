import socket
import sys

from utils import parse_method, parse_status_code, get_status_phrase


def handle_connection(connection: socket.socket, address):
    try:
        data = connection.recv(4096)
        if not data:
            return

        request = data.decode("utf-8")
        headers, _, body = request.partition("\r\n\r\n")
        headers = headers.split("\r\n")
        status_line = headers.pop(0)
        method = parse_method(status_line)
        status_code = parse_status_code(status_line)
        status_phrase = get_status_phrase(status_code)

        response_headers = [
            f"Request Method: {method}",
            f"Request Source: ({address[0]}, {address[1]})",
            f"Response Status: {status_code} {status_phrase}",
            *headers
        ]

        response = f"HTTP/1.1 {status_code} {status_phrase}\r\n" + \
                   "\r\n".join(response_headers) + \
                   "\r\n\r\n" + \
                   body

        connection.sendall(response.encode("utf-8"))
    finally:
        connection.close()


def start_server(host: str, port: int):
    """Start echo server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        while True:
            connection, address = server_socket.accept()
            print(f"Connection from {address}")
            handle_connection(connection, address)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:\n python echo_server.py <host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])
    start_server(host, port)
