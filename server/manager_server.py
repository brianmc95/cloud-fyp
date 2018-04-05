#!/usr/bin/env python3

"""
    Simple http server
"""

import http.server
import ssl
import json
import argparse
from DataManager import DataManager


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET/HEAD/POST commands.
    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.
    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.
    """

    httpd = None

    server_version = "SimpleHTTPWithUpload/"
    dm = DataManager()

    def do_POST(self):
        """Serve a POST request."""
        success = False
        if "/account/add/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.add_account(data)
                if result:
                    self.send_response(200)
                    self.end_headers()
                    success = True

        elif "/account/set/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.set_account(data["ACCOUNT_NAME"], data["PROVIDER"])
                if result:
                    self.send_response(200)
                    self.end_headers()
                    success = True

        elif "/account/list/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.get_accounts(data["PROVIDER"])
                if result:
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    success = True

        elif "/account/delete/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.delete_account(data["ACCOUNT_NAME"], data["PROVIDER"])
                if result:
                    self.send_response(200)
                    self.end_headers()
                    success = True

        elif "/deploy/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.deploy(data)
                if result:
                    self.send_response(200)
                    self.end_headers()
                    success = True

        elif "/deploy-options/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.deploy_options(data)
                if result:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    success = True

        elif "/key/" in self.path:
            data = self.read_request()
            if data:
                result = False
                if data["OPERATION"] == "UPLOAD":
                    result = self.dm.add_key(data)
                elif data["OPERATION"] == "DOWNLOAD":
                    result = self.dm.download_key(data["PROVIDER"], data["KEY_NAME"])
                elif data["OPERATION"] == "LIST":
                    result = self.dm.get_keys(data["PROVIDER"])
                elif data["OPERATION"] == "DELETE":
                    result = self.dm.delete_key(data["PROVIDER"], data["KEY_NAME"])
                if result:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    success = True

        elif "/migrate/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.migrate(data)
                if result:
                    self.send_response(200)
                    self.end_headers()
                    success = True

        elif "/monitor/" in self.path:
            data = self.read_request()
            if data:
                if data["CURRENT"]:
                    result = self.dm.get_current_data()
                else:
                    result = self.dm.get_specific_data(data["YEAR"], data["MONTH"], data["DAY"])
                if result:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    success = True

        elif "/addrecord/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.add_record(data)
                if result:
                    self.send_response(200)
                    self.end_headers()
                    success = True

        if not success:
            self.send_response(404)
            self.send_header("Content-Type", "html/text")
            self.end_headers()
        return

    def read_request(self):
        try:
            length = int(self.headers["content-length"])
            post_body = self.rfile.read(length).decode("utf-8", "ignore")
            print(post_body)
            data = json.loads(post_body)
            return data
        except json.JSONDecodeError as e:
            print(e)
            return None

def serve(ip, port, ssl_cert=None):
    server_address = (ip, port)

    httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
    if ssl_cert:
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=''.format(ssl_cert), server_side=True)
    print("Serving HTTP on {} port: {} with ssl certificate file {} ...".format(ip, port, ssl_cert))
    httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start cloud service')
    parser.add_argument("ip", help="IP Address of the central server in the system will run on")
    parser.add_argument("port", help="port the server is hosted on")
    parser.add_argument("ssl", help="SSL cert the server can use for encryption [Optional]", default=None)
    args = parser.parse_args()

    serve(args.ip, int(args.port), args.ssl)