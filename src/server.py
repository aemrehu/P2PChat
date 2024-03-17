import socket
import threading
import json
from pathlib import Path

class Server:
    def __init__(self):
        port = open(Path("src/server.txt")).read().split(':')[1]
        port = int(port)
        host = '0.0.0.0'

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.peers = {}  # Dict to keep track of connected peers
        self.index = 0

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

    def start_server(self):
        def accept_peers():
            while True:
                data, addr = self.sock.recvfrom(1024)
                if data.decode() == 'punch':
                    if addr not in self.peers.values():
                        self.peers[int(self.index)] = addr
                        self.index += 1
                    print(f"Punched hole for {addr}")
                if data.decode() == 'list':
                    # self.sock.sendto(json.dumps(self.peers).encode('ascii'), addr)
                    for i, peer in self.peers.items():
                        if peer != addr:
                            self.sock.sendto(f'{i}: {peer}'.encode('ascii'), addr)
                if data.decode().split(' ')[0] == 'peer':
                    i = int(data.decode().split(' ')[1])
                    self.sock.sendto(json.dumps(self.peers[i]).encode('ascii'), addr)

        threading.Thread(target=accept_peers).start()

if __name__ == "__main__":
    server = Server()
    threading.Thread(target=server.start_server).start()

    # wait for q to quit
    while True:
        if input() == 'q':
            exit()
