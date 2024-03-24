import sys
import os
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit
from PySide6.QtCore import QObject, Signal, Slot, Qt
import socket
import logging

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Configure logging
logpath = os.path.join(__location__[:-4], 'log')
os.makedirs(logpath, exist_ok=True)
logging.basicConfig(filename=os.path.join(logpath, 'qtclient.log'), level=logging.INFO,
                    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

class Communicator(QObject):
    message_received = Signal(str)

class ListenerThread(threading.Thread):
    def __init__(self, sock, communicator, main):
        super().__init__()
        self.sock = sock
        self.communicator = communicator
        self.main = main
        self.running = True
        self._tryagain = 3

    def run(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.communicator.message_received.emit(f"{addr}: {data.decode()}")
                logging.info(f"LISTENER: Received message from {addr}: {data.decode()}")
            except Exception as e:
                logging.error(f"LISTENER: {e}")
                if self._tryagain > 0:
                    self._tryagain -= 1
                    logging.info("LISTENER: Restarting listener")
                else:
                    self.stop()

    def stop(self):
        self.running = False
        logging.info("LISTENER: ListenerThread stopped")

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.serverIp, self.serverPort = open(os.path.join(__location__, 'server.txt')).read().split(":")
        self.serverPort = int(self.serverPort)

        self.sport = self.find_available_sender_port(50001, 60000)
        logging.info(f"Found and bound available port: {self.sport}")
        self.get_peer = False
        self.approved_peers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.sport))
        self.communicator = Communicator()
        self.listener = ListenerThread(self.sock, self.communicator, self)
        self.listener.daemon = True
        self.listener.start()
        logging.info("ListenerThread started")
        self.communicator.message_received.connect(self.append_message)

        self.setWindowTitle(f"Chat - {self.sport}")
        self.resize(500, 600)

        self.central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(self.central_widget)  # Set the central widget

        self.layout = QVBoxLayout(self.central_widget)  # Create a vertical layout for the central widget

        # Tab widget for managing different chats
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Add server tab
        self.server_widget = QTextEdit()
        self.server_widget.setReadOnly(True)
        self.tab_widget.addTab(self.server_widget, "Server")

        # self.client_threads = {}  # Dictionary to store ClientThread instances for each client
        self.tab_index_mapping = {}  # Dictionary to map tab index to client address
        self.tab_count = 0

        # self.tab_widget.currentChanged.connect(self.tab_changed)

        # Input box and sending button
        self.input_text = QLineEdit()
        self.layout.addWidget(self.input_text)

        self.send_button = QPushButton("Send")
        self.layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.send_message)
        self.input_text.returnPressed.connect(self.send_message)

        self.INSTRUCTIONS = "Type 'list' to get a list of available peers.\nType 'peer <number>' to initiate chat."

        logging.info("MainWindow initialized")

    def find_available_sender_port(self, start_port, end_port):
        for port in range(start_port, end_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.bind(('0.0.0.0', port))
                return port
            except OSError:
                pass
        logging.error("Could not find an available port in the range.")
        raise OSError("Could not find an available port in the range.")

    def connect_to_server(self):
        self.sock.sendto(b'punch', (self.serverIp, self.serverPort))
        self.approved_peers.append((self.serverIp, self.serverPort))
        self.tab_index_mapping[0] = (self.serverIp, self.serverPort)
        self.tab_count += 1
        logging.info(f"Connecting to server at {self.serverIp}:{self.serverPort}")

    def connect_to_peer(self, addr):
        ip, port = addr
        print(f"Connecting to peer {ip}:{port}")
        self.sock.sendto(b'punch', (ip, port))
        self.approved_peers.append((ip, port))
        self.tab_index_mapping[self.tab_count] = (ip, port)
        self.tab_count += 1
        widget = QTextEdit()
        widget.setReadOnly(True)
        self.tab_widget.addTab(widget, f"{ip}:{port}")
        logging.info(f"Connecting to peer at {ip}:{port}")

        print(self.tab_index_mapping)

    @Slot(str)
    def append_message(self, message):
        # Sort incoming messages to the correct tab
        sender_addr, message_text = message.split(": ", 1)
        sender_addr = (sender_addr.split(", ")[0].strip("\"\'[]()"), int(sender_addr.split(", ")[1].strip("\"\'[]()")))

        if self.get_peer:
            self.get_peer = False
            # print(message_text)
            address = message_text.split(", ")
            address = (address[0].strip("\"[]"), int(address[1].strip("\"[]")))
            self.connect_to_peer(address)
            return

        for tab_index, client_addr in self.tab_index_mapping.items():
            # print("tab_index", tab_index, "client_addr", client_addr, "sender_addr", sender_addr)

            if client_addr == sender_addr:
                # print("appending message")
                if 'punched' in message_text:
                    logging.info(f"Connect successful to {sender_addr}")
                    if tab_index == 0:
                        self.server_widget.append(f"{self.INSTRUCTIONS}")
                    return
                elif 'punch' in message_text:
                    self.sock.sendto("punched".encode(), sender_addr)
                    logging.info(f"Received punch from {sender_addr}")
                    return
                
                self.tab_widget.widget(tab_index).append(f"Them: {message_text}")
                return
        # If sender address not found in mapping, assume it's from the server
        # print("Tab not found, appending to server")
        if 'punched' in message_text:
            # self.server_widget.append(f"{sender_addr}: {message_text}")
            logging.info(f"Connect successful to {sender_addr}")
        elif 'punch' in message_text:
            self.sock.sendto("punched".encode(), sender_addr)
            logging.info(f"Received punch from {sender_addr}")
            self.server_widget.append(f"{sender_addr} wants to connect!")
        return

    def send_message(self):
        msg = self.input_text.text()
        if msg:
            if 'peer' in msg:
                self.get_peer = True
            current_tab_index = self.tab_widget.currentIndex()

            dest_addr = self.tab_index_mapping[current_tab_index]

            # Append the sent message to the appropriate widget
            if dest_addr == (self.serverIp, self.serverPort):
                self.server_widget.append(f"You: {msg}")
            else:
                for tab_index, client_addr in self.tab_index_mapping.items():
                    if client_addr == dest_addr:
                        self.tab_widget.widget(tab_index).append(f"You: {msg}")
                        break

            self.sock.sendto(msg.encode(), self.tab_index_mapping[current_tab_index])
            self.input_text.clear()
            logging.info(f"Sent message to {dest_addr}: {msg}")

    def closeEvent(self, event):
        logging.info("MainWindow closed")
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.connect_to_server()  # Replace with your server IP and port
    window.show()
    logging.info("MainWindow shown")
    sys.exit(app.exec())
