import socket
import sys
import threading

class Client:

    get_peer = False
    approved_peers = []
    dest_ip = ""
    sender_port = 0  # Sender port (50001 by default)
    dest_port = 50000  # Destination port
    sock = None

    def run(self):
        try:
            self.dest_ip = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            print("Hostname could not be resolved. Exiting")
            sys.exit()

        print(f"DEBUG: ip = {self.dest_ip}")
        print(f"DEBUG: port = {self.dest_port}")

        self.approved_peers.append((self.dest_ip, self.dest_port))

        print("Punching hole")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.sender_port = self.find_available_sender_port(50001, 60000)
        self.sock.bind(('0.0.0.0', self.sender_port)) # Bind to any available port
        print(f"DEBUG: binded to {self.dest_ip}:{self.sender_port}")
        
        self.sock.sendto(b'punch', (self.dest_ip, self.dest_port))
        print("Hole punched")

        listener = threading.Thread(target=self.listen, daemon=True)
        listener.start()

        self.send_msg()

    def find_available_sender_port(self, start_port, end_port):
        for port in range(start_port, end_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.bind(('0.0.0.0', port))
                return port
            except OSError:
                pass
        raise OSError("Could not find an available port in the range.")

    def listen(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            if self.get_peer:
                address = data.decode().split(", ")
                address = (address[0].strip("\"[]"), int(address[1].strip("\"[]")))
                self.connect_to_peer(address)
                self.get_peer = False
            if addr in self.approved_peers:
                print(f"{addr}: {data.decode()}")

    def connect_to_peer(self, address):
        self.sock.sendto(b'punch', address)
        print(f"Punched hole for {address}")

        self.approved_peers.append(address)

        self.dest_ip = address[0]
        self.dest_port = address[1]

        print(f"DEBUG: {self.dest_ip}, {self.dest_port}")

    def send_msg(self):
        while True:
            msg = input('> ')
            self.sock.sendto(msg.encode(), (self.dest_ip, self.dest_port))

            if msg == 'peer':
                self.get_peer = True


if __name__ == "__main__":
    client = Client()
    client.run()
