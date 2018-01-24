#!/usr/bin/python3.6

"""
    Brian McCarthy 114302146
    brianmccarthy95@gmail.com

    Script designed to be deployed to cloud instances to monitor their current status
    such as CPU, memory, disk and network usages. Then send a report to a central server

    Example report
    {
        "INSTANCE_ID": 1,
        "INSTANCE_NAME": "test1",
        "DATE_TIME": "22-1-18 17:30:00",
        "DISK_USAGE": {
            "/dev/vdb": {
                "TOTAL": 105555197952,
                "FREE": 100107202560
            },
            "/dev/vda1": {
                "TOTAL": 4156795699,
                "FREE": 40012431360
            },
            "/dev/vdc": {
                "TOTAL": 105555197952,
                 "FREE": 100107202560
        },
        "NET_USAGE": {
                "PACKETS_SENT": 3,
                "BYTES_SENT": 706,
                "BYTES_RECV": 198,
                "CONNECTIONS": 4,
                "PACKETS_RECV": 3
        },
        "MEM_USAGE": {
            "TOTAL": 4143718400,
            "AVAIL": 3770216448
        },
        "CPU_USAGE": 0.3
    }
"""

import psutil
import json
from datetime import datetime
import requests


class Monitor:

    report = None

    def __init__(self, id, name, server_ip, server_port):
        self.instance_id = id
        self.instance_name = name
        self.server_ip = server_ip
        self.server_port = server_port
        self.previous_net_usage = None

    def gen_report(self):
        # Get all our usage information and generate a report based on this.

        today = datetime.now()
        now = today.strftime("%Y-%m-%d %H:%M:%S")

        report = {"INSTANCE_ID": self.instance_id,
                  "INSTANCE_NAME": self.instance_name,
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

        if self.previous_net_usage == None:
            report["NET_USAGE"]["BYTES_RECV"] = network_usage.bytes_recv
            report["NET_USAGE"]["BYTES_SENT"] = network_usage.bytes_sent
            report["NET_USAGE"]["PACKETS_SENT"] = network_usage.packets_sent
            report["NET_USAGE"]["PACKETS_RECV"] = network_usage.packets_recv
        else:
            report["NET_USAGE"]["BYTES_RECV"] = network_usage.bytes_recv - self.previous_net_usage.bytes_recv
            report["NET_USAGE"]["BYTES_SENT"] = network_usage.bytes_sent - self.previous_net_usage.bytes_sent
            report["NET_USAGE"]["PACKETS_SENT"] = network_usage.packets_sent - self.previous_net_usage.packets_sent
            report["NET_USAGE"]["PACKETS_RECV"] = network_usage.packets_recv - self.previous_net_usage.packets_recv

        self.previous_net_usage = network_usage
        report["NET_USAGE"]["CONNECTIONS"] = connections

        self.report = report

    def send_report(self):
        """  http://127.0.0.1:8081/addrecord/  """

        url = "http://{}:{}/addrecord/".format(self.server_ip, self.server_port)
        r = requests.post(url=url, json=self.report) # Requests deals with converting to json2
        print(r.status_code)


def main():
    mon = Monitor(2, "betty", "127.0.0.1", 8081)
    mon.gen_report()
    mon.send_report()


if __name__ == "__main__":
    main()
