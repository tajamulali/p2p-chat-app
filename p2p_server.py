import socket
import threading
from database import setup_db, register_user, validate_login

class P2PServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        setup_db()  # Initialize the database
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"P2P Server started on {self.host}:{self.port}")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=self.handle_peer, args=(client_socket,)).start()

    def handle_peer(self, client_socket):
        while True:
            try:
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break

                command, *args = request.split()
                response = "Invalid command"

                if command == "REGISTER":
                    username, password = args
                    if register_user(username, password):
                        response = "Registration successful"
                    else:
                        response = "Username already exists"

                elif command == "LOGIN":
                    username, password = args
                    if validate_login(username, password):
                        response = "Login successful"
                    else:
                        response = "Invalid credentials"

                client_socket.send(response.encode('utf-8'))

            except Exception as e:
                print(f"Error handling peer: {str(e)}")
                break

        client_socket.close()

def main():
    p2p_server = P2PServer("0.0.0.0", 9999)
    p2p_server.start()

if __name__ == "__main__":
    main()
