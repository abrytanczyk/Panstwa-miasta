import socket
import struct

class Client:
    def __init__(self, host, port, room_number):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.room = room_number

        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
        self.s.connect(self.addr)

        # send selected room number
        self.s.send(str.encode(str(room_number)))

        # get categories from server
        cat_as_bytes = self.s.recv(1024)
        cat_string = cat_as_bytes.decode()
        if cat_string == "No rooms available":
            exit()

        self.categories = cat_string.rstrip(';').split(';')

        # get multicast port from server
        multicast_port_as_bytes = self.s.recv(1024)
        self.multicast_port = multicast_port_as_bytes.decode()

        self.time_addr = '239.0.0.1'
        self.time_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.time_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.time_s.bind(('', int(self.multicast_port)))
        self.time_s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack("4sl", socket.inet_aton(self.time_addr), socket.INADDR_ANY))

    def disconnect(self):
        self.s.close()

    def send(self, message):
        message = str(self.room) + ';' + message
        data = str.encode(message)
        self.s.send(data)

    def get_time(self):
        data_as_bytes = self.time_s.recv(10240)
        return int(data_as_bytes.decode())