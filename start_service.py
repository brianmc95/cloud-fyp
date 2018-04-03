import argparse
from server import manager_server
from dashboard import index

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start cloud management service')
    parser.add_argument('ip', help='HTTP Server IP')
    parser.add_argument('port', type=int, help='Listening port for management server')
    parser.add_argument('ssl', help='Include location of SSL cert if you want security', action='store', nargs='?')
    args = parser.parse_args()

    manager_server.serve(args.ip, args.port, args.ssl)
    #index.serve(True)

