import socket
import threading
import json

class P2PChat:
    def __init__(self, host='127.0.0.1', port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)  # Increase the backlog value to allow more pending connections
        self.peers = []  # List to keep track of connected peers

    def handle_peer(self, peer, addr):
        while True:
            data = peer.recv(1024).decode('ascii')
            if not data:
                break
            print(f"Received message from {addr}: {data}")

    def broadcast_presence(self):
        while True:
            presence_msg = json.dumps({'host': self.host, 'port': self.port})
            for peer in self.peers:
                try:
                    peer.send(presence_msg.encode('ascii'))
                except Exception as e:
                    print(f"Error broadcasting presence: {e}")
                    self.peers.remove(peer)

            # Sleep for a while before broadcasting again
            threading.Event().wait(10)

    def accept_peers(self):
        while True:
            peer, addr = self.sock.accept()
            threading.Thread(target=self.handle_peer, args=(peer, addr)).start()
            self.peers.append(peer)

    def start_p2p_chat(self):
        threading.Thread(target=self.accept_peers).start()
        threading.Thread(target=self.broadcast_presence).start()

        while True:
            dest_host = input("Enter destination host: ")
            dest_port = int(input("Enter destination port: "))
            msg = input("Enter message: ")

            dest_address = (dest_host, dest_port)
            msg = f"{self.host}:{self.port} says: {msg}"
            for peer in self.peers:
                try:
                    peer.send(json.dumps({'dest_address': dest_address, 'message': msg}).encode('ascii'))
                except Exception as e:
                    print(f"Error sending message to peer: {e}")
                    self.peers.remove(peer)

if __name__ == "__main__":
    chat = P2PChat()
    chat.host, chat.port = chat.sock.getsockname()
    threading.Thread(target=chat.start_p2p_chat).start()
