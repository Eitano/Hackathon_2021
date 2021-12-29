import socket
import struct
import threading
import time
import concurrent.futures
import random
import multiprocessing
import scapy.all


def wake_up_call(socket_udp, port_udp=13117):
    threading.Timer(1.0, wake_up_call, args=[socket_udp]).start()
    # open brodcast
    msg = struct.pack('Ibh', 0xabcddcba, 0x2, 2081)
    socket_udp.sendto(msg, ("<broadcast>", port_udp))


def start_game(client_side):
    returned_answer = None
    # set 10 sec for a game
    client_side.settimeout(10) 
    try:
        
        # recive answer from client
        returned_answer = client_side.recv(1024).decode("utf-8")
    except:
        pass
    return returned_answer


def play_():

    def send_open_msg(client1, client2, msg, upd_, tcp_):
        exception_flag = False
        try:  
            # sending message to all clients
            client1.sendall(msg)
            client2.sendall(msg)

        except:
            client1.close()
            client2.close()
            exception_flag = True

        if exception_flag:
            # close socket as well 
            upd_.close()
            tcp_.close()

        return exception_flag

    def send_finish_msg(client1, client2, msg, upd_, tcp_):
        # sending message to all clients
        client1.sendall(msg)
        client2.sendall(msg)
        client1.close()
        client2.close() 
        upd_.close()
        tcp_.close()

    while True:
        # -------------LET-THE-GAME-BEGIN-------------#
        server_ip = scapy.all.get_if_addr("eth1") # get the ip
        port_tcp = 2081 
        port_udp = 13117

        print("Server started,listening on IP address {}".format(server_ip))

        # set socket
        upd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # setsockopt - set the socket options
        upd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        upd_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        upd_socket.bind((str(server_ip), port_udp))

        # use threading sending brodcast to udp socket
        make_suggestion = multiprocessing.Process(target=wake_up_call, args=(upd_socket,))
        make_suggestion.start()

        global tcp_socket #seting global veriable
        
        # setting tcp socket as we have done erlier for udp socket
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.bind(('', port_tcp))

        tcp_socket.listen(2) # listen for 2 clients
        # The concurrent.futures module provides a high-level interface for asynchronously executing callables.
        with concurrent.futures.ThreadPoolExecutor(2) as executor:
            
            while True:
                # Accept a connection. The socket must be bound to an address and listening for connections.
                # The return value is a pair (conn, address)
                # where conn is a new socket object usable to send and receive data on the connection
                # and address is the address bound to the socket on the other end of the connection.
                client_side_1, address_client_1 = tcp_socket.accept()
                team_name_1 = client_side_1.recv(1024).decode("utf-8")

                client_side_2, address_client_2 = tcp_socket.accept()
                team_name_2 = client_side_2.recv(1024).decode("utf-8")

                time.sleep(2) 

                # Generate equations
                while True:
                    x = random.randint(0,9)
                    y = random.randint(0,9)
                    z = random.randint(0,9)
                    k = random.randint(0,9)
                    res = x + y - 2*z - k
                    if 0 <= res < 10:
                        question = '{} + {} -2 *{} - {}= '.format(x, y, z , k)
                        answer = str(res)
                        break

                open_msg = '\x1b[6;30;41m' + '\nWelcome to Quick Maths.\n' + '\x1b[0m'
                open_msg += '\x1b[6;30;42m' + '\nPlayer 1: {}'.format(team_name_1) + '\x1b[0m'
                open_msg += '\x1b[5;30;45m' + '\nPlayer 2: {}'.format(team_name_2) + '\x1b[0m'
                open_msg += '\x1b[7;30;44m' + "\nPlease answer the following question as fast as you can:\n" + '\x1b[0m'
                open_msg += '\x1b[6;30;47m' + "\nHow much is {} ?".format(question) +' \x1b[0m'
                open_msg = bytes(open_msg, "utf-8")

                exception_returned = send_open_msg(client_side_1, client_side_2, open_msg, upd_socket, tcp_socket)
                if exception_returned:
                    break

                # An abstract class that provides methods to execute calls asynchronously
                # get the result of the executor
                client_1_result, time_taken_c1 =  client_1_result.result().split(',')
                client_2_result, time_taken_c2 =  client_2_result.result().split(',')                

                # check if clients disconnected before gaming means result is ''
                if client_1_result == '' or client_2_result == '': 
                    try:
                        client_side_1.close()
                        client_side_2.close()                        
                    except:
                        continue
                    upd_socket.close()
                    tcp_socket.close()
                    break

                # if None of the clients return result
                if client_1_result == 'None' and client_2_result == 'None':

                    draw = '\x1b[7;30;43m' + '\nGame over!\n' + '\x1b[0m'
                    draw += '\x1b[7;30;43m' + "\nThe correct answer was {}!\n".format(answer) + '\x1b[0m'
                    draw += '\x1b[7;30;43m' + "\nIt's a draw!\n" + '\x1b[0m'
                    draw = bytes(draw, "utf-8")

                    # call send_finish_msg send draw to all and close them
                    send_finish_msg(client_side_1, client_side_2, draw, upd_socket, tcp_socket)
                    break


                # if one of the client answer correct he is the winner else the other is win
               
                if time_taken_c1 < time_taken_c2:
                    if client_1_result == answer:
                        winner = team_name_1
                    else:
                        winner = team_name_2
                else:
                    if client_2_result == answer:
                        winner = team_name_2
                    else:
                        winner = team_name_1

                game_summary =  '\x1b[6;30;44m' + "\nGame over!\n" + '\x1b[0m'
                game_summary += '\x1b[6;30;44m' + "\nThe correct answer was {}!\n".format(answer) + '\x1b[0m'
                game_summary += '\x1b[6;30;44m' + "\nCongratulations to the winner: {}\n".format(winner) + '\x1b[0m'
                game_summary = bytes(game_summary, "utf-8")

                # call send_finish_msg send summary to all and close them
                send_finish_msg(client_side_1, client_side_2, game_summary, upd_socket, tcp_socket)
                break

if __name__ == '__main__':
    play_()

  
