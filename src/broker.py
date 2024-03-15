import socket
import threading
import json

class Broker:
    def __init__(self, host='0.0.0.0', port=50000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        # self.sock.listen(5)  # Increase the backlog value to allow more pending connections
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
                data, addr = self.sock.recvfrom(1024)
                if data.decode() == 'punch':
                    if addr not in self.peers:
                        self.peers.append(addr)
                    print(f"Punched hole for {addr}")
                if data.decode() == 'list':
                    self.sock.sendto(json.dumps(self.peers).encode('ascii'), addr)
                if data.decode() == 'peer':
                    for peer in self.peers:
                        if peer != addr:
                            self.sock.sendto(json.dumps(peer).encode('ascii'), addr)
                            break

                # peer, address = self.sock.accept()
                # self.peers.append([peer, address])
                # threading.Thread(target=self.handle_peer, args=(peer,)).start()

        threading.Thread(target=accept_peers).start()

if __name__ == "__main__":
    broker = Broker()
    threading.Thread(target=broker.start_broker).start()

    # wait for q to quit
    while True:
        if input() == 'q':
            break
