import sys
import os
import threading
import socket
import time
import uuid
import struct
import datetime
from datetime import timezone
from _thread import *

# https://bluesock.org/~willkg/dev/ansi.html
ANSI_RESET = "\u001B[0m"
ANSI_RED = "\u001B[31m"
ANSI_GREEN = "\u001B[32m"
ANSI_YELLOW = "\u001B[33m"
ANSI_BLUE = "\u001B[34m"

# Our Colors
ANSI_PURPLE = "\u001B[35m"
Bold_Purple = "\033[1;35m"
Bold_Yellow = "\033[1;33m"
SKY_BLUE = "\033[96m"
BRIGHT_RED = "\033[1;91m"

_NODE_UUID = str(uuid.uuid4())[:8]


def print_yellow(msg):
    print(f"{ANSI_YELLOW}{msg}{ANSI_RESET}")


def print_blue(msg):
    print(f"{ANSI_BLUE}{msg}{ANSI_RESET}")


def print_red(msg):
    print(f"{ANSI_RED}{msg}{ANSI_RESET}")


def print_green(msg):
    print(f"{ANSI_GREEN}{msg}{ANSI_RESET}")


# Our color prints:

def print_purple(msg):
    print(f"{ANSI_PURPLE}{msg}{ANSI_RESET}")


def print_cyan(msg):
    print(f"{SKY_BLUE}{msg}{ANSI_RESET}")


def print_bold_yellow(msg):
    print(f"{Bold_Yellow}{msg}{ANSI_RESET}")


def print_bold_purple(msg):
    print(f"{Bold_Purple}{msg}{ANSI_RESET}")


def print_bright_red(msg):
    print(f"{BRIGHT_RED}{msg}{ANSI_RESET}")


def get_broadcast_port():
    return 35498


def get_node_uuid():
    return _NODE_UUID


class NeighborInfo(object):
    def __init__(self, delay, broadcast_count, ip=None, tcp_port=None):
        # Ip and port are optional, if you want to store them.
        self.delay = delay
        self.broadcast_count = broadcast_count
        self.ip = ip
        self.tcp_port = tcp_port
        # if self.broadcast_count:
        # self.count += 1
        # else:
        # self.count = 1


#################################
# OUR CODE  #####################
#################################


neighbor_information = {}
# Global TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Global UDP socket
broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

true = 1


def send_broadcast_thread():
    print_cyan("*" * 50)
    print_cyan("Started sending broadcasts")
    print_cyan("*" * 50)
    node_uuid = get_node_uuid()
    udp_port = get_broadcast_port()
    broadcaster.bind(('10.0.2.255', udp_port))
    random_tcp_port = server.getsockname()[1]

    while True:
        broadcast = node_uuid + " ON " + str(random_tcp_port)
        print_bold_purple(f"broadcast message = {broadcast}")

        linux_broadcast_address = "10.0.2.255"

        sock_address = (linux_broadcast_address, udp_port)
        broadcaster.sendto(bytes(broadcast, 'utf-8'), sock_address)
        # broadcast_time = time.time()
        # print_sky(broadcast_time)
        # daemon_thread_builder(receive_broadcast_thread(), ())
        time.sleep(1)


def receive_broadcast_thread():
    # udp_port = get_broadcast_port()
    # broadcaster.connect(("10.0.2.255",udp_port))
    # print("binded")
    node_uuid = get_node_uuid()
    while True:
        data, (ip, udp_port) = broadcaster.recvfrom(4096)
        broadcast = data.decode("utf-8")
        info = broadcast.split(" ")
        uuid = info[0]
        recv_port = info[2]
        if uuid == node_uuid:
            pass
        else:
            print_cyan("*" * 50)
            print("Started receiving broadcasts from other nodes")
            print_cyan("*" * 50)
            print_blue(f"RECV: {data} FROM: {ip}:{udp_port}")

            print_bold_yellow(f"uuid = {uuid}")
            print_bold_yellow(f"TCP port = {recv_port}")
            print("*" * 50)
            if uuid in neighbor_information.keys():
                info_object = neighbor_information[uuid]
                count = getattr(info_object, 'broadcast_count')
                newcount = count + 1
                if (newcount % 10) == 0:
                    exchanging_thread = daemon_thread_builder(exchange_timestamps_thread(uuid, ip, recv_port), ())
                    exchanging_thread.start()
                else:
                    setattr(info_object, 'broadcast_count', newcount)
                    #print_green(f"Broadcast count :{newcount} ")
            else:

                exchanging_thread = daemon_thread_builder(exchange_timestamps_thread(uuid, ip, recv_port), ())
                exchanging_thread.start()
                # exchanging_thread.join()

        break


def tcp_server_thread():
    sock, address = server.accept()
    print_purple("Connection is accepted ")
    timestamp = datetime.datetime.utcnow().timestamp()
    sock.sendall(struct.pack('!f', timestamp))
    sock.close()
    print_purple("Connection is closed ")


def exchange_timestamps_thread(other_uuid: str, other_ip: str, other_tcp_port: int):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (other_ip, int(other_tcp_port))
    print_bright_red(f"ATTEMPTING TO CONNECT TO {other_uuid} ")
    print("*" * 50)
    tcp_client.connect((server_address))
    print_purple("Connected!")
    timestamp_at_connection_time = datetime.datetime.utcnow().timestamp()
    received_timestamp = tcp_client.recv(512)
    print_purple("TS received!")
    [x] = struct.unpack('!f', received_timestamp)
    print_bold_yellow(f"Received timestamp is:{x} ")
    print_bold_yellow(f"Timestamp at connection time is:{timestamp_at_connection_time}")
    delay = x - timestamp_at_connection_time
    this_uuid = get_node_uuid()
    print_bold_yellow(f"Delay from {other_uuid} to {this_uuid} = {delay}")
    newcount = 1
    #print_green(f"Broadcasts count :{newcount} ")
    NodeA = NeighborInfo(delay, newcount, other_ip, other_tcp_port)
    neighbor_information[other_uuid] = NodeA

    pass


def daemon_thread_builder(target, args=()) -> threading.Thread:
    th = threading.Thread(target=target, args=args)
    # th.setDaemon(True)
    return th


def entrypoint():
    print("Entered entry point")
    server.setblocking(0)
    server.bind(('10.0.2.15', 0))
    server.listen()

    sending_broadcast_thread = threading.Thread(target=send_broadcast_thread)
    sending_broadcast_thread.start()
    while true:
        try:
            recv_broadcast_thread = daemon_thread_builder(tcp_server_thread())
            recv_broadcast_thread.start()


        except:
            receiving_broadcast_thread = daemon_thread_builder(receive_broadcast_thread())
            receiving_broadcast_thread.start()

    pass


###########################################
############################################


def main():
    print("*" * 50)
    print_red("To terminate this program use: CTRL+C")
    print_red("If the program blocks/throws, you have to terminate it manually.")
    print_green(f"NODE UUID: {get_node_uuid()}")
    print("*" * 50)
    time.sleep(2)  # Wait a little bit.
    entrypoint()


if __name__ == "__main__":
    main()
