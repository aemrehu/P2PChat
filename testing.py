import socket
import threading

class P2PChat:
    def __init__(self, host='127.0.0.1', port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)  # Increase the backlog value to allow more pending connections
        self.clients = []  # List to keep track of client connections

    def handle_client(self, client):
        while True:
            data = client.recv(1024).decode('ascii')
            if not data:
                break
            print("Received message: ", data)

    def start_chat(self):
        def accept_clients():
            while True:
                client, address = self.sock.accept()
                self.clients.append(client)
                threading.Thread(target=self.handle_client, args=(client,)).start()

        threading.Thread(target=accept_clients).start()

        while True:
            msg = input("Enter message: ")
            for client in self.clients:
                client.send(msg.encode('ascii'))

if __name__ == "__main__":
    chat = P2PChat()
    chat.start_chat()