import threading
from server import manager_server
from dashboard import index
import json

if __name__ == "__main__":

    try:
        file = open("config/manager-config.json")
        config = json.load(file)
        ip = config["internal-ip"]
        port = config["port"]
        ssl = config["ssl-cert"]

        manager = threading.Thread(target=manager_server.run, args=(ip, port, ssl,))
        dash = threading.Thread(target=index.serve, args=(False,))
        dash.start()
        manager.start()
    except json.JSONDecodeError as e:
        print("ERROR: Could not load json file")
    except IOError as e:
        print("ERROR: Could not open json config file cloud-fyp/config/manager-config.json must be available")


