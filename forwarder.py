#!/usr/bin/python


from socket import *
import threading
import sys
import hosts


def create_sock(ip_ver, fwdr_host, fwdr_port):
    addr = (fwdr_host, fwdr_port)

    if has_dualstack_ipv6() and ip_ver == "6":
        sock = create_server(addr, family=AF_INET6, dualstack_ipv6=True)
    else:
        sock = create_server(addr, family=AF_INET)

    return sock


def start_forwarder(ip_ver, fwdr_socket, fwdr_port):
    if ip_ver == "6":
        server_ip = hosts.SERVER_IP_V6
    else:
        server_ip = hosts.SERVER_IP_V4

    fwdr_socket.listen()

    print(f"Forwarder listening on port {fwdr_port}...")

    if fwdr_port == 8022:
        dest_port = hosts.SERVER_PORT_SSH
    elif fwdr_port == 8080:
        dest_port = hosts.SERVER_PORT_HTTP
    elif fwdr_port == 8000:
        dest_port = 8888

    accept_conn(fwdr_socket, server_ip, dest_port)


def accept_conn(fwdr_socket, dest_host, dest_port):
    while True:
        recv_sock, recv_addr = fwdr_socket.accept()
        print(f"Initiated TCP connection with {recv_addr}")

        if sys.argv[1] == "6":
            send_sock = socket(AF_INET6, SOCK_STREAM)
            send_sock.connect((dest_host, dest_port, 0, 0))
        else:
            send_sock = socket(AF_INET, SOCK_STREAM)
            send_sock.connect((dest_host, dest_port))
        
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

            if not data:
                break

            dest_socket.send(data)
        except Exception as e:
            print("Client disconnected")
            break

    src_socket.close()
    dest_socket.close()


def main():
    ip_version = sys.argv[1]

    print(f"Forwarder running in IPv{ip_version} mode\n")

    f_sock_ssh = create_sock(ip_version, hosts.FORWARDER_IP, hosts.FORWARDER_LISTEN_PORT_SSH)
    f_sock_http = create_sock(ip_version, hosts.FORWARDER_IP, hosts.FORWARDER_LISTEN_PORT_HTTP)
    f_sock_echo = create_sock(ip_version, hosts.FORWARDER_IP, hosts.FORWARDER_LISTEN_PORT_ECHO)

    ssh_thread = threading.Thread(target=start_forwarder, args=(ip_version, f_sock_ssh, hosts.FORWARDER_LISTEN_PORT_SSH,))
    http_thread = threading.Thread(target=start_forwarder, args=(ip_version, f_sock_http, hosts.FORWARDER_LISTEN_PORT_HTTP,))
    echo_thread = threading.Thread(target=start_forwarder, args=(ip_version, f_sock_echo, hosts.FORWARDER_LISTEN_PORT_ECHO,))
    
    socks = [ssh_thread, http_thread, echo_thread]

    for sock in socks:
        sock.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        exit(0)
