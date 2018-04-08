#!/usr/bin/env python3

"""
    Simple http server
"""

import http.server
import ssl
import json
import logging
from server.DataManager import DataManager


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
    logger = logging.getLogger(__name__)

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
                    self.logger.info("Successfully added an account")
                    success = True

        elif "/account/set/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.set_account(data["ACCOUNT_NAME"], data["PROVIDER"])
                if result:
                    self.send_response(200)
                    self.end_headers()
                    self.logger.info("Successfully set an account")
                    success = True

        elif "/account/list/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.get_accounts(data["PROVIDER"])
                if result:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    self.logger.info("Successfully sent deployment information")
                    success = True

        elif "/account/delete/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.delete_account(data["ACCOUNT_NAME"], data["PROVIDER"])
                if result:
                    self.send_response(200)
                    self.end_headers()
                    self.logger.info("Successfully deleted an account")
                    success = True

        elif "/deploy/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.deploy(data)
                if result:
                    self.send_response(200)
                    self.end_headers()
                    self.logger.info("Successfully deployed node")
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
                    self.logger.info("Successfully sent deployment information")
                    success = True

        elif "/delete-node/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.delete_node(data)
                if result:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    self.logger.info("Successfully sent deployment information")
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
                    self.logger.info("Successfully dealt with key request")
                    success = True

        elif "/migrate/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.migrate(data)
                if result:
                    self.send_response(200)
                    self.end_headers()
                    self.logger.info("Migration successfully begun")
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
                    self.logger.info("Successfully sent monitoring data")
                    success = True

        elif "/addrecord/" in self.path:
            data = self.read_request()
            if data:
                result = self.dm.add_record(data)
                if result:
                    self.send_response(200)
                    self.end_headers()
                    self.logger.info("Success in adding a record")
                    success = True

        if not success:
            self.logger.info("Request could not be successfully handled")
            self.send_response(404)
            self.send_header("Content-Type", "html/text")
            self.end_headers()
        return

    def read_request(self):
        try:
            self.logger.info("Request recieved from: {}".format(self.headers["client_address"]))
            self.logger.info("Path of request: {}".format(self.path))
            length = int(self.headers["content-length"])
            post_body = self.rfile.read(length).decode("utf-8", "ignore")
            data = json.loads(post_body)
            self.logger.info("Request data is {}".format(data))
            return data
        except json.JSONDecodeError as e:
            self.logger.exception("Message could not be decoded into JSON")
            return None

def run(ip, port, ssl_cert=None):
    server_address = (ip, int(port))

    httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
    if ssl_cert:
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=''.format(ssl_cert), server_side=True)
    print("Serving HTTP on {} port: {} with ssl certificate file {} ...".format(ip, port, ssl_cert))
    httpd.serve_forever()
