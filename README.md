# P2PChat
Peer-to-peer chat application for local networks.

Run one instance of the server, which will give out peer addresses to communicate directly.


## How to start
Clone the repository and follow instructions below.


## Client

### Installation
We recommend to create a virtual environment.

    python -m venv <venv>

Install package

    pip install -e .

Create a file called `server.txt` in the `client/src` folder.

In the file type the IP-address and port of the server you want to connect to:

    <IPADDRESS>:<PORT>

### Run
Run the client from command line:

    python qtclient.py

Client UI will open in a separate window.


## Server
Create a file called `server.txt` in the `server/src` folder.

In the file type the IP-address and port where you want to run the server:

    <IPADDRESS>:<PORT>

### Run
Run the server from command line:

    python server.py

