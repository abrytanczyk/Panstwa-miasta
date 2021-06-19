#import clientGUI
import socket
import argparse


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.addr = (host, port)

        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
        self.s.connect(self.addr)

        # get categories form server
        cat_as_bytes = self.s.recv(1024)
        cat_string = cat_as_bytes.decode()
        self.categories = cat_string.rstrip(';').split(';')

        multicast_addr_as_bytes = self.s.recv(1024)
        self.multicast_addr = multicast_addr_as_bytes.decode()

    def disconnect(self):
        self.s.close()

    def send(self, message):
        data = str.encode(message)
        self.s.send(data)


"""
parser = argparse.ArgumentParser()
parser.add_argument("ip_add", help="Server's ip address")
parser.add_argument("port_number", help="Server's port number")
args = parser.parse_args()

HOST = args.ip_add
PORT = int(args.port_number)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect((HOST, PORT))

# get categories form server
cat_as_bytes = s.recv(1024)
cat_string = cat_as_bytes.decode()
categories = cat_string.rstrip(';').split(';')

multicast_addr_as_bytes = s.recv(1024)
multicast_addr = multicast_addr_as_bytes.decode()

print(multicast_addr)

"""

# display gui
# clientGUI.show_window(categories)
# clientGUI.update_window()

# TODO remove client in server
# s.close()
