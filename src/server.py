import socket
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Server:
    def __init__(self):
        port = open(Path("src/server.txt")).read().split(':')[1]
        port = int(port)
        host = '0.0.0.0'

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.settimeout(0.5)
        self.peers = {}  # Dict to keep track of connected peers
        self.index = 0

        logging.info('Server initialized')

    def run(self):
        logging.info('Server is running')
        while True:
            try:
                try:
                    data, addr = self.sock.recvfrom(1024)
                except socket.timeout:
                    continue
                logging.info(f"Received {data.decode()} from {addr}")
                if data.decode() == 'punch':
                    if addr not in self.peers.values():
                        self.peers[int(self.index)] = addr
                        self.index += 1
                        self.sock.sendto('punched'.encode('ascii'), addr)
                        logging.info(f"Punched hole for {addr}")
                        print(f"Punched hole for {addr}")
                if data.decode() == 'list':
                    # self.sock.sendto(json.dumps(self.peers).encode('ascii'), addr)
                    for i, peer in self.peers.items():
                        if peer != addr:
                            self.sock.sendto(f'{i}: {peer}'.encode('ascii'), addr)
                    logging.info(f"Sent list of peers to {addr}")
                if data.decode().split(' ')[0] == 'peer':
                    i = int(data.decode().split(' ')[1])
                    self.sock.sendto(json.dumps(self.peers[i]).encode('ascii'), addr)
                    logging.info(f"Sent peer {i} to {addr}")
            except KeyboardInterrupt:
                logging.info('Server stopped')
                break

if __name__ == "__main__":
    server = Server()
    server.run()
