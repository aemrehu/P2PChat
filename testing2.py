import socket
import threading
import json

class Broker:
    def __init__(self, host='127.0.0.1', port=6000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)  # Increase the backlog value to allow more pending connections
        self.peers = []  # List to keep track of connected peers

    def handle_peer(self, peer):
        while True:
            data = peer.recv(1024).decode('ascii')
            if not data:
                break

            data = json.loads(data)

            if 'list' in data:
                # Handle list data
                peer.send(json.dumps(self.peers).encode('ascii'))
                continue

            print(f"Received message from {peer.getpeername()}: {data}")

    def start_broker(self):
        def accept_peers():
            while True:
                peer, address = self.sock.accept()
                self.peers.append(peer)
                threading.Thread(target=self.handle_peer, args=(peer,)).start()

        threading.Thread(target=accept_peers).start()

if __name__ == "__main__":
    broker = Broker()
    threading.Thread(target=broker.start_broker).start()

    class P2PChat:
        def __init__(self, host='127.0.0.1', port=5000, broker_host='127.0.0.1', broker_port=6000):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((broker_host, broker_port))
            self.host = host
            self.port = port
            self.clients = []  # List to keep track of connected clients

            # Register with the broker
            self.sock.send(json.dumps({'host': self.host, 'port': self.port}).encode('ascii'))

        def handle_client(self, client):
            while True:
                data = client.recv(1024).decode('ascii')
                if not data:
                    break
                print("Received message: ", data)

        def start_chat(self, dest_host, dest_port, msg):
            dest_address = (dest_host, dest_port)
            msg = f"{self.host}:{self.port} says: {msg}"
            self.sock.send(json.dumps({'dest_address': dest_address, 'message': msg}).encode('ascii'))

        def receive_messages(self):
            while True:
                data = self.sock.recv(1024).decode('ascii')
                print("Received message: ", data)

        def connect_to_peer(self, peer_info):
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((peer_info['host'], peer_info['port']))
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,)).start()

        def start_p2p_chat(self):
            threading.Thread(target=self.receive_messages).start()

            while True:
                dest_host = input("Enter destination host: ")
                dest_port = int(input("Enter destination port: "))
                msg = input("Enter message: ")
                self.start_chat(dest_host, dest_port, msg)

    chat = P2PChat()
    threading.Thread(target=chat.start_p2p_chat).start()
