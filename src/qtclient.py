import sys
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit
from PySide6.QtCore import QObject, Signal, Slot, Qt
import socket

class Communicator(QObject):
    message_received = Signal(str)

class ListenerThread(threading.Thread):
    def __init__(self, sock, communicator, main):
        super().__init__()
        self.sock = sock
        self.communicator = communicator
        self.main = main
        self.running = True

    def run(self):
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            self.communicator.message_received.emit(f"{addr}: {data.decode()}")

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.brokerIp = "192.168.10.37"
        self.brokerPort = 50000

        self.sport = 50003
        self.get_peer = False
        self.approved_peers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.sport))
        self.communicator = Communicator()
        self.listener = ListenerThread(self.sock, self.communicator, self)
        self.listener.daemon = True
        self.listener.start()
        self.communicator.message_received.connect(self.append_message)

        self.setWindowTitle("Chat Application")

        self.central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(self.central_widget)  # Set the central widget

        self.layout = QVBoxLayout(self.central_widget)  # Create a vertical layout for the central widget

        # Tab widget for managing different chats
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Add broker tab
        self.broker_widget = QTextEdit()
        self.tab_widget.addTab(self.broker_widget, "Broker")

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

    def connect_to_broker(self):
        self.sock.sendto(b'punch', (self.brokerIp, self.brokerPort))
        self.approved_peers.append((self.brokerIp, self.brokerPort))
        self.tab_index_mapping[0] = (self.brokerIp, self.brokerPort)
        self.tab_count += 1

    def connect_to_peer(self, addr):
        ip, port = addr
        print(f"Connecting to peer {ip}:{port}")
        self.sock.sendto(b'punch', (ip, port))
        self.approved_peers.append((ip, port))
        self.tab_index_mapping[self.tab_count] = (ip, port)
        self.tab_count += 1
        self.tab_widget.addTab(QTextEdit(), f"{ip}:{port}")

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

        for tab_index, client_addr in self.tab_index_mapping.items():
            # print("tab_index", tab_index, "client_addr", client_addr, "sender_addr", sender_addr)

            if client_addr == sender_addr:
                # print("appending message")
                self.tab_widget.widget(tab_index).append(f"Them: {message_text}")
                return
        # If sender address not found in mapping, assume it's from the broker
        # print("Tab not found, appending to broker")
        if 'punch' in message_text:
            self.broker_widget.append(f"{sender_addr}: {message_text}")

    def send_message(self):
        msg = self.input_text.text()
        if msg:
            if 'peer' in msg:
                self.get_peer = True
            current_tab_index = self.tab_widget.currentIndex()

            dest_addr = self.tab_index_mapping[current_tab_index]

            # Append the sent message to the appropriate widget
            if dest_addr == (self.brokerIp, self.brokerPort):
                self.broker_widget.append(f"You: {msg}")
            else:
                for tab_index, client_addr in self.tab_index_mapping.items():
                    if client_addr == dest_addr:
                        self.tab_widget.widget(tab_index).append(f"You: {msg}")
                        break

            self.sock.sendto(msg.encode(), self.tab_index_mapping[current_tab_index])
            self.input_text.clear()

    def closeEvent(self, event):
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.connect_to_broker()  # Replace with your server IP and port
    window.show()
    sys.exit(app.exec())
