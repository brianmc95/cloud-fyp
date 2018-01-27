#!/usr/bin/python3.6

"""
    Brian McCarthy 114302146
    brianmccarthy95@gmail.com

    Script designed to be deployed to cloud instances to monitor their current status
    such as CPU, memory, disk and network usages. Then send a report to a central server
"""

import psutil
import argparse
from datetime import datetime
import requests
import time

PREVIOUS_NET_USAGE = None


def start_record(IP, port, ID, name):
    while True:
        report = gen_report(ID, name)
        send_report(report, IP, port)
        time.sleep(300)

def gen_report(instance_id, instance_name):
    # Get all our usage information and generate a report based on this.

    global PREVIOUS_NET_USAGE

    today = datetime.now()
    now = today.strftime("%Y-%m-%d %H:%M:%S")

    report = {"INSTANCE_ID": instance_id,
              "INSTANCE_NAME": instance_name,
              "DATE_TIME": now,
              "CPU_USAGE": psutil.cpu_percent(interval=5),
              "MEM_USAGE": {"TOTAL": None,
                            "AVAIL": None},
              "DISK_USAGE": {},
              "NET_USAGE": {"BYTES_RECV": None,
                            "BYTES_SENT": None,
                            "PACKETS_SENT": None,
                            "PACKETS_RECV": None,
                            "CONNECTIONS": None}
              }

    memory_usage = psutil.virtual_memory()
    report["MEM_USAGE"]["TOTAL"] = memory_usage.total
    report["MEM_USAGE"]["AVAIL"] = memory_usage.available

    for disk in psutil.disk_partitions(all=False):
        disk_usage = psutil.disk_usage(disk.mountpoint)
        report["DISK_USAGE"][disk.device] = {"TOTAL": disk_usage.total, "FREE": disk_usage.free}

    network_usage = psutil.net_io_counters()
    connections = len(psutil.net_connections())

    if PREVIOUS_NET_USAGE is None:
        PREVIOUS_NET_USAGE = network_usage
        time.sleep(60)

    report["NET_USAGE"]["BYTES_RECV"] = network_usage.bytes_recv - PREVIOUS_NET_USAGE.bytes_recv
    report["NET_USAGE"]["BYTES_SENT"] = network_usage.bytes_sent - PREVIOUS_NET_USAGE.bytes_sent
    report["NET_USAGE"]["PACKETS_SENT"] = network_usage.packets_sent - PREVIOUS_NET_USAGE.packets_sent
    report["NET_USAGE"]["PACKETS_RECV"] = network_usage.packets_recv - PREVIOUS_NET_USAGE.packets_recv

    PREVIOUS_NET_USAGE = network_usage
    report["NET_USAGE"]["CONNECTIONS"] = connections

    return report


def send_report(report, server_ip, server_port):
    # Send the generated report to the central server
    url = "http://{}:{}/addrecord/".format(server_ip, server_port)
    r = requests.post(url=url, json=report)  # Requests deals with converting to json2
    if r.status_code != 200:
        print("Report failed to send")
        print(report)


def main():
    parser = argparse.ArgumentParser(description='Send monitor reports')
    parser.add_argument("--ip", help="IP Address of the central server in the system that records the usages")
    parser.add_argument("--port", "-p", help="port the server is hosted on")
    parser.add_argument("--id", help="id of the instance which is sending the monitoring information")
    parser.add_argument("--name", "-n", help="name of the instance which is sending monitoring information")

    args = parser.parse_args()

    start_record(args.ip, args.port, args.id, args.name)


if __name__ == "__main__":
    main()
