import socket
import random
import string
import select
import threading
import time
import re
import argparse


def message_categories(cat):
    msg = ''
    for c in cat:
        msg += c + ';'
    msg_as_bytes = str.encode(msg)
    return msg_as_bytes


def categories_for_room():
    categories = ['Państwo','Miasto']
    additional = ['Rzeka','Imię','Zwierzę','Książka','Film','Rzecz','Kolor','Zawód','Góra']
    categories.extend(random.sample(additional,3))
    return categories


def prepare_rooms():
    rooms = []
    sockets = []
    tmp = 1
    # 5 rooms
    for i in range(5):
        tmp_port = '500' + str(tmp)
        cat = categories_for_room()
        rooms.append([i,0,tmp_port,cat])
        # id, number of clients, multicast port, categories, answers
        tmp += 1
        sockets.append([])
    return rooms,sockets


def get_room(rooms,number):
    clients_max_number = 5
    if rooms[number][1] < clients_max_number:
        rooms[number][1] += 1
        return rooms[number]
    return -1


def get_letter():
    return random.choice(string.ascii_lowercase)


# this function should run in separate thread for each started game
def time_server(MCAST_PORT):
    MCAST_GRP = '239.0.0.1'
    MULTICAST_TTL = 2
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,MULTICAST_TTL)
    a = 60
    while a > 0:
        sock.sendto(str.encode(str(a)),(MCAST_GRP,int(MCAST_PORT)))
        time.sleep(1)
        a -= 1


def get_score(socket,room_number):
    for client in sockets_in_room[room_number]:
        if client[0] == socket:
            return client[-1]


def save_score(room_number):
    for client in sockets_in_room[room_number]:
        score = 0
        answers = client[1:]
        client_id = client[0]
        answers_others = []
        for i in range(5):
            answers_others.append([])
        for client_others in sockets_in_room[room_number]:
            if client_others[0] == client_id:
                continue
            else:
                for i in range(5):
                    if client_others[i + 1] == '':
                        continue
                    answers_others[i].append(client_others[i + 1])
        for i in range(5):
            if answers[i] == '':
                continue
            if answers_others[i].count(answers[i]) >= 1:
                score += 5
            elif len(answers_others[i]) == 0:
                score += 15
            else:
                score += 10
        client.append(score)


def get_client(socket):
    for room in sockets_in_room:
        for client in room:
            if client[0] == socket:
                return client


def send_score(socket):
    client = get_client(socket)
    socket.send(str(client[-1]).encode())


parser = argparse.ArgumentParser()
parser.add_argument("port_number",help="Server's port number")
args = parser.parse_args()

# socket to listen
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)

# to change or get by argument
HOST = ''
PORT = int(args.port_number)

rooms,sockets_in_room = prepare_rooms()


server_socket.bind((HOST,PORT))
server_socket.listen()
socket_list = [server_socket]

while True:
    to_read,to_write,in_error = select.select(socket_list,[],[],0)

    for s in to_read:
        # server - accept new connections
        if s == server_socket:
            s_conn,addr = server_socket.accept()
            number_as_bytes = s_conn.recv(512)
            number = int(number_as_bytes.decode())
            room = get_room(rooms,number)
            if room == -1:
                s_conn.send(str.encode("No rooms available"))
                s_conn.close()
            else:
                sockets_in_room[room[0]].append([s_conn])
                cat = room[3]
                s_conn.send(message_categories(cat))
                # send multicast port
                s_conn.send(str.encode(room[2]))
                socket_list.append(s_conn)

        # clients send answers or starting the game
        else:
            data_as_bytes = s.recv(1024)
            if data_as_bytes:
                data = data_as_bytes.decode()
                # starting game when server received "[room_nr];Start Game"
                if re.search("^[0-9]+;Start Game",data):
                    # send letter to all players in room and start thread with multicast
                    l = get_letter()
                    room_number = int(data.split(';')[0])
                    print("start, letter: " + l)
                    for client in sockets_in_room[room_number]:
                        client[0].send(str.encode(l))
                    # start sending time
                    t = threading.Thread(target=time_server,args=(rooms[room_number][2],))
                    t.start()

                # answers
                else:
                    # save answers
                    print(data)
                    room_number = int(data.split(';')[0])
                    answers = data[:-1].split(';')[1:]
                    print(answers)
                    clients_answered = 0
                    for client in sockets_in_room[room_number]:
                        if len(client) == 6:
                            clients_answered += 1
                        else:
                            if client[0] == s:
                                client.extend(answers)
                                clients_answered += 1
                    print(sockets_in_room[room_number])
                    print(clients_answered)
                    # check if it was the last client (answer) in room
                    if clients_answered == len(sockets_in_room[room_number]):
                        save_score(room_number)
                        # send answered to all client in room and close sockets
                        for client in sockets_in_room[room_number]:
                            send_score(client[0])
                            socket_list.remove(client[0])
                            client[0].close()
                        sockets_in_room[room_number].clear()
            else:
                s.close()
                socket_list.remove(s)

    for s in in_error:
        print('enter error')
        s.close()
        socket_list.remove(s)

server_socket.close()
