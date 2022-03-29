#!/usr/bin/python


from socket import *
import ssl


def create_sec_sock(serv_host, serv_port):
    certfile = "cert/domain.crt"
    keyfile = "cert/domain.key"

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    context.load_cert_chain(
        certfile,
        keyfile
    )

    if has_dualstack_ipv6():
        sock = create_server((serv_host, serv_port), family=AF_INET6, dualstack_ipv6=True)
    else:
        sock = create_server((serv_host, serv_port), family=AF_INET)

    sec_sock = context.wrap_socket(sock, server_side=True)

    return sec_sock


def start_server(serv_sock):
    listen_host = ""
    listen_port = 8888

    with serv_sock as sock:
        # sock.bind((listen_host, listen_port))
        sock.listen()

        print(f"Echo server listening on port {listen_port}...")

        clnt_conn, clnt_addr = sock.accept()

        with clnt_conn:
            while True:
                try:
                    data = clnt_conn.recv(1024)

                    if not data:
                        break

                    print(f"[ RECEIVED FROM {clnt_addr} ] {data.decode('utf-8')}")
                except:
                    break


def main():
    listen_host = ""
    listen_port = 8888

    s_sock = create_sec_sock(listen_host, listen_port)
    start_server(s_sock)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        exit(0)
