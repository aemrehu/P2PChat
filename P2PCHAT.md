## Corporate/Industry track

Aleksi Rehu – corporate track <br> 
Santeri Heikkinen – corporate track <br>
Tomi Pantsar – corporate track<br>


# P2P Chat Application

## About the project

Our project is a decentralized Peer-to-Peer (P2P) chat application for local networks. The system allows multiple clients to communicate directly with each other without relying on a central server for message routing. Instead, the role of server is limited to providing clients with essential connection information to establish direct communication with each other. Communication between clients is facilitated using UDP hole punching, allowing for connections to be established even behind NAT devices.


## Implemented components:

Our system architecture consists of nodes each with an assigned role as either as client, or the server. Each node operates as an independent entity within the distributed network environment. 

Each node comprehensively logs its behavior, including messages, events, and other actions to keep track of system monitoring and troubleshooting. This includes timestamps, name, logging level, and the message itself.

Node roles:<br>
**Server node:**
* The server node serves as a mediator of sort whose only function is to share enough information between client nodes for them to be able to establish communication, such as IP address and port number. After this no communication related data is transferred through the server.
* The server node also maintains record of all inbound and outbound traffic, alongside monitoring changes on server level, e.g. server initializations. 
* Available commands for the server node are:
    - `punch`-> return `punched` to acknowledge connection
    - `list` -> return list of all connected users to the network
    - `peer <number>` -> return address of peer
* There is only one server node in the system. 

**Client nodes:**
* Each client represents a user interacting with with the system. These nodes initiate communication through the use of UDP hole punching, send messages, and receive responses from other clients. 
* The client node also maintains record of connection confirmations, all messages sent and received alongside matching timestamps. 
* Available commands for the client nodes are:
    - `punch` -> return `punched` to acknowledge connection
* The number of clients can be an arbitrary number from 2 and above.

---
Relevant principles covered in the course for our application:

Architecture:
* System architecture used in the project is decentralized, no central server or authority controls network
* Structured in a peer-to-peer manner, -||- 

Processes: 
* Client thread utilization
* Client-server relation

Communication:
* Sockets via UDP to establish connection
---

## Built with:
- Python 3 libraries
    - sys
    - threading
    - socket
    - pathlib
    - logging
    - json
- Third party libraries
    - PySide6 by Qt
        - chat GUI implementation
- Packaged with simple Python setup and installation with Pip


## Getting Started:

### Create *server.txt* file to provide server address

    IPADDRESS:PORT

### Run server on any machine

    python server.py

### Install client dependencies

Can be installed in a virtual environment.

    pip install -e .

### Run client/s

    python qtclient.py


## Results of the tests:

### System throughput
We ran tests by sending `1000` messages through the system and were able to conclude an average time per 1000 messages at `6 milliseconds`

* **6 ms / 1000 messages**

Rest of the testing is still underway.
