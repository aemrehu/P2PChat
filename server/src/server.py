import socket
import logging
import json
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Configure logging
logpath = os.path.join(__location__[:-4], 'log')
os.makedirs(logpath, exist_ok=True)
logging.basicConfig(filename=os.path.join(logpath, 'server.log'), level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Server:
    def __init__(self):
        try:
            host, port = open(os.path.join(__location__, 'server.txt')).read().split(':')
            port = int(port)
        except Exception as e:
            logging.error(f"Failed to read server.txt: {e}")
            raise e

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.settimeout(0.5)
        self.peers = {}  # Dict to keep track of connected peers
        self.index = 0

        logging.info('Server initialized')

    def run(self):
        logging.info(f'Server is running at {self.sock.getsockname()}')
        print(f'Server is running at {self.sock.getsockname()}')
        while True:
            try:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    logging.info(f"Received {data.decode()} from {addr}")
                except socket.timeout:
                    continue
                if data.decode() == 'punch':
                    if addr not in self.peers.values():
                        self.peers[int(self.index)] = addr
                        self.index += 1
                        self._send('punched', addr)
                        logging.info(f"Punched hole for {addr}")
                        print(f"Punched hole for {addr}")
                if data.decode() == 'list':
                    if len(self.peers) <= 1:
                        logging.info("No peers to send")
                    else:
                        try:
                            for i, peer in self.peers.items():
                                if peer != addr:
                                    self._send(f'{i}: {peer}', addr)
                            logging.info(f"Sent list of peers to {addr}")
                        except Exception as e:
                            logging.error(f"Failed to send peers: {e}")
                if data.decode().split(' ')[0] == 'peer':
                    try:
                        i = int(data.decode().split(' ')[1])
                        self._send(json.dumps(self.peers[i]), addr)
                        logging.info(f"Sent peer {i} to {addr}")
                    except Exception as e:
                        logging.error(f"{e}")
            except KeyboardInterrupt:
                logging.info('Server stopped')
                break

    def _send(self, message, address):
        try:
            self.sock.sendto(message.encode('ascii'), address)
            logging.info(f"Sent {message} to {address}")
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

if __name__ == "__main__":
    server = Server()
    server.run()
