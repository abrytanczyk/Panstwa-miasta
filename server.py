import socket
import random
import string
import select


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
    # 5 rooms for each room seperate multicast address?
    for i in range(5):
        tmp_addr = '239.0.0.' + str(tmp)
        cat = categories_for_room()
        rooms.append([i, 0, tmp_addr, cat])
        # id, number of clients, multicast address, categories, answers
        tmp += 1
        sockets.append([])
    return rooms, sockets


def get_room(rooms, number):
    clients_max_number = 5
    if rooms[number][1] < clients_max_number:
        rooms[number][1] += 1
        return rooms[number]
    return -1


def get_letter():
    return random.choice(string.ascii_lowercase)


def leave_game():
    # close all sockets in room,
    pass


def get_score(socket, room_number):
    fd = socket.fileno()
    for client in sockets_in_room[room_number]:
        if client[0] == fd:
            return client[-1]


def save_score(room_number):
    for client in sockets_in_room[room_number]:
        score = 0
        answers = client[1:]
        print(answers)
        client_id = client[0]
        answers_others = []
        for i in range(5):
            answers_others.append([])
        for client_others in sockets_in_room[room_number]:
            if client_others[0] == client_id:
                continue
            else:
                for i in range(5):
                    if client_others[i+1] == '':
                        continue
                    answers_others[i].append(client_others[i+1])
        print(answers_others)
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
        print(client)


# socket to listen
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)

# to change or get by argument
HOST = '127.0.0.1'
PORT = 12345

rooms, sockets_in_room = prepare_rooms()

#need socket with multicast for every room

server_socket.bind((HOST,PORT))

server_socket.listen()

socket_list = [server_socket]

while True:
    to_read, to_write, in_error = select.select(socket_list, [], [], 0)

    for s in to_read:
        # server - accept new connections
        if s == server_socket:
            s_conn, addr = server_socket.accept()
            number_as_bytes = s_conn.recv(512)
            number = int(number_as_bytes.decode())
            room = get_room(rooms, number)
            if room == -1:
                s_conn.send(str.encode("No rooms available"))
                s_conn.close()
            else:
                #sockets_in_room.append([s_conn,room[0]])
                sockets_in_room[room[0]].append([s_conn.fileno()])
                cat = room[3]
                #print(addr)
                #print(cat)
                #print(room)
                #print(sockets_in_room)
                s_conn.send(message_categories(cat))
                # send multicast address
                s_conn.send(str.encode(room[2]))
                socket_list.append(s_conn)

        # clients send answers or starting the game
        else:
            data_as_bytes = s.recv(1024)
            if data_as_bytes:
                data = data_as_bytes.decode()
                # starting game
                if data == "Start Game":
                    # send letter to all players in room
                    print("start")
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
                            if client[0] == s.fileno():
                                client.extend(answers)
                                clients_answered += 1
                    print(sockets_in_room[room_number])
                    print(clients_answered)
                    # check if it was the last client (answer) in room - maybe not necessary
                    if clients_answered == len(sockets_in_room[room_number]):
                        save_score(room_number)
            else:
                s.close()
                socket_list.remove(s)

    # send score
    for s in to_write:
        s.send("wynik")
        # close sockets

    for s in in_error:
        print(s)


server_socket.close()

'''
while True:
    s_conn, addr = s_listen.accept()
    if addr not in clients: # maybe check only ip_addr without port number?
        room = get_room(rooms)
        if room == -1:
            print("nie ma wolnych pokoi")
            s_conn.close()
        else:
            clients.append([room[1], addr])
            # send categories
            cat = room[2]
            s_conn.send(message_categories(cat))
            # send multicast address
            s_conn.send(str.encode(room[1]))

            print(addr)
            print(clients)


            # temporally - next client cannot connect until server receive this message
            # for every message quick connect and send?
            # maybe sending time and letters on multicast
            answer_as_bytes = s_conn.recv(1024)
            answer = answer_as_bytes.decode()
            print(answer)


s_listen.close()
'''
# unassigned ip addresses multicast - 224.0.0.151-224.0.0.250
# use 239.0.0.1 -
