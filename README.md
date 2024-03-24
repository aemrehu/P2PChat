# P2PChat

## How to start

### Installation
We recommend to create a virtual environment.

    python -m venv <venv>

Install package

    pip install -e .

Create a file called `server.txt` in the `src` folder. Both the server and client need this file.

In the file type the IP-address and port where you want to run the server:

    <IPADDRESS>:<PORT>

### Server
Run the server from command line:

    python src/server.py

### Client
Run the client from command line:

    python src/qtclient.py

Client UI will open in a separate window.
