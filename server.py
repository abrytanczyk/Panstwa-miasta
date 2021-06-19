import socket
import random
import string


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
    tmp = 151
    # 5 rooms for each room seperate multicast address?
    for i in range(5):
        tmp_addr = '224.0.0.' + str(tmp)
        cat = categories_for_room()
        answers = []
        for c in cat:
            answers.append([])
        rooms.append([0, tmp_addr, cat, answers])
        # number of clients, multicast address, categories
        tmp += 1
    return rooms


def get_room(rooms):
    clients_max_number = 10
    for r in rooms:
        if r[0] < clients_max_number:
            r[0] += 1
            return r
    return -1


def get_letter():
    return random.choice(string.ascii_lowercase)


# socket to listen
s_listen = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)

# to change or get by argument
HOST = '127.0.0.1'
PORT = 12345

clients = []
rooms = prepare_rooms()

#need socket with multicast for every room

s_listen.bind((HOST, PORT))

s_listen.listen()

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

# unassigned ip addresses multicast - 224.0.0.151-224.0.0.250
