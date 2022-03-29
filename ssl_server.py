#!/usr/bin/python


from socket import *
import ssl


def create_sec_sock():
    certfile = "cert/domain.crt"
    keyfile = "cert/domain.key"

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    context.load_cert_chain(
        certfile,
        keyfile
    )

    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    
    sec_sock = context.wrap_socket(sock, server_side=True)

    return sec_sock


def start_server(serv_sock):
    listen_host = ""
    listen_port = 8888

    with serv_sock as sock:
        sock.bind((listen_host, listen_port))
        sock.listen()

        clnt_conn, clnt_addr = sock.accept()

        with clnt_conn:
            while True:
                data = clnt_conn.recv(1024)

                if not data:
                    break

                print(f"[ RECEIVED FROM {clnt_addr} ] {data.decode('utf-8')}")


def accept_conn(serv_sock):
    while True:
        try:
            clnt_conn, clnt_addr = serv_sock.accept()
        except Exception as e:
            print(e)
    
        data = clnt_conn.recv(1024)

        print(f"[ RECEIVED from {clnt_addr} ] {data.decode('utf-8')}")


def main():
    s_sock = create_sec_sock()
    start_server(s_sock)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        exit(0)
