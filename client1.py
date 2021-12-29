import socket
import struct
import getch
import signal
import time


def play_():
    print("Client started, listening for offer requests...")
    port_udp = 13117
    getch_timeout = 10

    def inter_timeout(signum, frame):
        pass

    signal.signal(signal.SIGALRM, inter_timeout)

    while True:
        # establish udp socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(('', port_udp))
        
        data_recived = None
        
        while True:
            # print(udp_socket.recvfrom(1024))
            data_recived, addrees = udp_socket.recvfrom(1024)
            if data_recived is None:
                continue
            try:
                unpack_data = struct.unpack('ibh', data_recived)
                if unpack_data[0] == -1412571974 and unpack_data[1] == 2:
                    break
            except:
                continue
        
        udp_socket.close()
        portnum = unpack_data[2]

        msg = "Received offer from {}".format(str(addrees[0]))
        msg += " attempting to connect..."
        print(msg)
        try:
            # setting a tcp socket
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.connect((socket.gethostname(), portnum))
            break

        except:
            tcp_socket.close()
            

    team_name = 'client_1\n'
    tcp_socket.sendall(bytes(team_name, "utf-8"))
    print(tcp_socket.recv(1024).decode("utf-8"))

    start = time.time()
    char = None
    try:
        signal.alarm(getch_timeout)
        char = getch.getch()
        signal.alarm(0)
    except:
        char = None

    message = char
    tcp_socket.sendall(bytes('{}, {}'.format(message, time.time() - start), "utf-8"))

    server_message = tcp_socket.recv(1024)

    # print the result from server
    message_from_server = server_message.decode("utf-8")
    print(message_from_server)
    # then close tcp conn
    tcp_socket.close()

if __name__ == '__main__':
    while True:
        play_()
