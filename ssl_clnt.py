#!/usr/bin/python

from socket import *
import ssl


def create_sec_sock():
    certfile = "cert/domain.crt"
    keyfile = "cert/domain.key"

    sock = socket(AF_INET, SOCK_STREAM, 0)

    sec_sock = ssl.wrap_socket(sock, keyfile=keyfile, certfile=certfile)

    return sec_sock


def main():
    clnt_sock = create_sec_sock()

    server_host = "192.168.1.83"
    server_port = 8000

    with clnt_sock as sock:
        sock.connect((server_host, server_port))

        while True:
            msg = input("Send: ")

            sock.sendall(msg.encode('utf-8'))
            
            if msg == ":q":
                sock.close()
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        exit(0)
