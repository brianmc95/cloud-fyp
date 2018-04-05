import argparse
import threading
from server import manager_server
from dashboard import index


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start cloud service')
    parser.add_argument("ip", help="IP Address of the central server in the system will run on")
    parser.add_argument("port", help="port the server is hosted on")
    parser.add_argument("--ssl", help="SSL cert the server can use for encryption [Optional]", default=None)
    args = parser.parse_args()

    manager = threading.Thread(target=manager_server.run, args=(args.ip, args.port, args.ssl,))
    dash = threading.Thread(target=index.serve, args=(False,))
    dash.start()
    manager.start()


