#!/usr/bin/python3

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
import json

def get_prev_report():
    prev_report = None
    try:
        prev_report = json.load(open("monitor/prev_report.json"))
    except json.JSONDecodeError as e:
        print(e)
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    return prev_report

def write_prev_net(report):
    with open('monitor/prev_report.json', 'w') as fp:
        json.dump(report, fp)

def gen_report(instance_id, provider, previous_report):
    # Get all our usage information and generate a report based on this.

    today = datetime.now()
    now = today.strftime("%Y-%m-%d %H:%M:%S")

    memory_usage = psutil.virtual_memory()
    report = {"INSTANCE_ID" : instance_id,
              "DATE_TIME"   : now,
              "CPU_USAGE"   : psutil.cpu_percent(interval=5),
              "MEM_TOTAL"   : memory_usage.total,
              "MEM__AVAIL"  : memory_usage.available,
              "DISK_USAGE"  : {},
              "CONNECTIONS" : None,
              "PACKETS_RECV": None,
              "PACKETS_SENT": None,
              "BYTES_SENT"  : None,
              "BYTES_RECV"  : None,
              "PROVIDER"    : provider
              }

    for disk in psutil.disk_partitions(all=False):
        disk_usage = psutil.disk_usage(disk.mountpoint)
        report["DISK_USAGE"][disk.device] = {"INSTANCE_ASSIGNED_ID": instance_id,
                                             "DATETIME": now,
                                             "PROVIDER": provider,
                                             "TOTAL": disk_usage.total,
                                             "FREE": disk_usage.free}

    network_usage = psutil.net_io_counters()
    connections = len(psutil.net_connections())

    if previous_report is None:
        previous_report = report
        previous_report["BYTES_RECV"] = network_usage.bytes_recv
        previous_report["BYTES_SENT"] = network_usage.bytes_sent
        previous_report["PACKETS_SENT"] = network_usage.packets_sent
        previous_report["PACKETS_RECV"] = network_usage.packets_recv
        time.sleep(60)

    network_usage = psutil.net_io_counters()
    report["BYTES_RECV"] = network_usage.bytes_recv - previous_report["BYTES_RECV"]
    report["BYTES_SENT"] = network_usage.bytes_sent - previous_report["BYTES_SENT"]
    report["PACKETS_SENT"] = network_usage.packets_sent - previous_report["PACKETS_SENT"]
    report["PACKETS_RECV"] = network_usage.packets_recv - previous_report["PACKETS_RECV"]

    report["CONNECTIONS"] = connections

    write_prev_net(report)

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
    parser.add_argument("--provider", "-pv", help="The provider this instance is running on.")

    args = parser.parse_args()

    previous_report = get_prev_report()
    report = gen_report(args.id, args.provider, previous_report)
    send_report(report, args.ip, args.port)


if __name__ == "__main__":
    main()
