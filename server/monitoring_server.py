# !/usr/bin/env python3.6

# File is in essence an updated to python3 version of the server found in the below link
# https://gist.github.com/mafayaz/faf938a896357c3a4c9d6da27edcff08

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import argparse
import re
import json
from server.DataManager import DataManager
# TODO: Add some exception handling for parsing json so we don't have constant errors.
# TODO: Add some logging to this so it doesn't just sit and do stuff without people knowing


class HTTPRequestHandler(BaseHTTPRequestHandler):

    dm = DataManager()

    def do_POST(self):
        if re.search("/addrecord/", self.path) is not None:
            if self.headers["Content-Type"] == "application/json":
                # Decode the message from the instance
                length = int(self.headers["content-length"])
                post_body = self.rfile.read(length).decode("utf-8", "ignore")

                result = self.dm.add_record(post_body)

                if result:
                    self.send_response(200)
                    self.end_headers()
                else:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
        else:
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer:
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.waitForThread()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    args = parser.parse_args()

    server = SimpleHttpServer(args.ip, args.port)
    print('HTTP Server Running...........')
    server.start()
    server.waitForThread()
