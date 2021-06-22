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
    tmp = 1
    # 5 rooms for each room seperate multicast address?
    for i in range(5):
        tmp_addr = '239.0.0.' + str(tmp)
        cat = categories_for_room()
        answers = []
        for c in cat:
            answers.append([])
        rooms.append([i, 0, tmp_addr, cat, answers])
        # id, number of clients, multicast address, categories, answers
        tmp += 1
    return rooms


def get_room(rooms, number):
    clients_max_number = 5
    if rooms[number][1] < clients_max_number:
        rooms[number][1] += 1
        return rooms[number]
    return -1


def get_letter():
    return random.choice(string.ascii_lowercase)


def leave_game():
    pass


# socket to listen
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)

# to change or get by argument
HOST = '127.0.0.1'
PORT = 12345

rooms = prepare_rooms()

#need socket with multicast for every room

server_socket.bind((HOST,PORT))

server_socket.listen()

connected_sockets = []
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
                connected_sockets.append([s_conn, room[0]])
                cat = room[3]
                #print(addr)
                #print(cat)
                #print(room)
                print(connected_sockets)
                s_conn.send(message_categories(cat))
                # send multicast address
                s_conn.send(str.encode(room[2]))
                socket_list.append(s_conn)

        # clients send answers
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
                    # check if it was the last client (answer) in room
            else:
                s.close()
                socket_list.remove(s)

    # send score
    for s in to_write:
        s.send("wynik")

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
