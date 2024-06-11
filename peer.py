import socket
import threading
import json
from rsa import generate_rsa_keys, sign_rsa
from database import save_message

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.peers = {}
        self.username = None
        self.public_key = None
        self.private_key = None
        print(f"Peer started on {self.host}:{self.port}")

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=self.handle_connection, args=(client_socket,)).start()

    def handle_connection(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    print(f"Received message: {message}")
                else:
                    client_socket.close()
                    break
            except Exception as e:
                print(f"Error handling connection: {str(e)}")
                client_socket.close()
                break

    def register(self, username, password, server_address):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(server_address)
            client_socket.send(f"REGISTER {username} {password}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(response)

    def login(self, username, password, server_address):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(server_address)
            client_socket.send(f"LOGIN {username} {password}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(response)
            if response == "Login successful":
                self.username = username
                self.public_key, self.private_key = generate_rsa_keys()
                return True
            return False

    def connect_to_peer(self, peer_address):
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect(peer_address)
        self.peers[peer_address] = peer_socket

    def send_message(self, peer_address, message):
        if peer_address in self.peers:
            peer_socket = self.peers[peer_address]
            signature = sign_rsa(self.private_key, self.username)  # Sign the hash of the username
            signed_message = {
                'message': message,
                'signature': signature,
                'username': self.username
            }
            peer_socket.send(json.dumps(signed_message).encode('utf-8'))
            save_message(self.username, message)
        else:
            print("Peer not connected")

def main():
    host = "127.0.0.1"
    base_port = 8888
    server_address = ("127.0.0.1", 9999)

    while True:
        try:
            port = int(input(f"Enter a unique port number for this peer (default {base_port}): ") or base_port)
            peer = Peer(host, port)
            break
        except OSError:
            print(f"Port {port} is already in use, please choose another one.")
            base_port += 1

    while True:
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            peer.register(username, password, server_address)

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            if peer.login(username, password, server_address):
                print("Login successful! You can now send and receive messages.")
                threading.Thread(target=peer.start).start()
                break

        elif choice == "3":
            break

    while True:
        print("1. Connect to peer")
        print("2. Send message")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            peer_host = input("Enter peer's host address: ")
            peer_port = int(input("Enter peer's port: "))
            peer.connect_to_peer((peer_host, peer_port))

        elif choice == "2":
            peer_host = input("Enter peer's host address: ")
            peer_port = int(input("Enter peer's port: "))
            message = input("Enter message: ")
            peer.send_message((peer_host, peer_port), message)


        elif choice == "3":
            break

if __name__ == "__main__":
    main()
