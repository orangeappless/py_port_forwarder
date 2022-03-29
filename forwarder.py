#!/usr/bin/python


from socket import *
import threading
import hosts


def create_sock():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    return sock


def start_forwarder(fwdr_socket):
    listen_host = hosts.FORWARDER_IP
    listen_port = hosts.FORWARDER_LISTEN_PORT

    fwdr_socket.bind((listen_host, listen_port))
    fwdr_socket.listen()

    print(f"Forwarder listening on port {listen_port}...")

    accept_conn(fwdr_socket)


def accept_conn(fwdr_socket):
    while True:
        try:
            recv_sock, src_addr = fwdr_socket.accept()
            print(f"Initiated TCP connection with {src_addr}")
        except:
            print(f"Error connecting with {src_addr}")

        send_sock = socket(AF_INET, SOCK_STREAM)
        send_sock.connect((hosts.SERVER_IP, hosts.SERVER_PORT))
        
        try:
            src_to_dest = threading.Thread(target=forward_data, args=(recv_sock, send_sock,))
            dest_to_src = threading.Thread(target=forward_data, args=(send_sock, recv_sock,))

            src_to_dest.start()
            dest_to_src.start()
        except:
            print("Error forwarding data")


def forward_data(src_socket, dest_socket):
    while True:
        try:
            data = src_socket.recv(1024)
            dest_socket.send(data)
        except:
            print("Client or remote server disconnected")
            break

    src_socket.close()
    dest_socket.close()


def main():
    f_sock = create_sock()
    start_forwarder(f_sock)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        exit(0)
