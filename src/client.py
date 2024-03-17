import socket
import sys
import threading

class Client:

    sport = 50002

    get_peer = False

    approved_peers = []

    ip = "192.168.10.37"
    dport = 50000

    sock = None

    def __init__(self) -> None:
        pass

    def run(self):
        # print("Please enter the server's IP address and port in the format 'ip:port'")
        # address = input()
        # self.ip, port = address.split(":")
        # self.dport = int(port)
        self.approved_peers.append((self.ip, self.dport))

        print("Punching hole")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.sport))
        self.sock.sendto(b'punch', (self.ip, self.dport))

        print("Hole punched")

        listener = threading.Thread(target=self.listen, daemon=True)
        listener.start()

        self.send_msg()

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

    def connect_to_peer(self, addr):
        self.sock.sendto(b'punch', addr)
        print(f"Punched hole for {addr}")

        self.approved_peers.append(addr)

        self.ip = addr[0]
        self.dport = addr[1]

        print(f"DEBUG: {self.ip}, {self.dport}")

    def send_msg(self):
        while True:
            msg = input('> ')
            self.sock.sendto(msg.encode(), (self.ip, self.dport))

            if 'peer' in msg:
                self.get_peer = True


if __name__ == "__main__":
    client = Client()
    client.run()
