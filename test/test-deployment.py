# !/usr/bin/env python3.6

from accounts.OpenStack import OpenStackProvider
from accounts.AWS import AWS
import argparse
import sys


def main():
    os_prov = OpenStackProvider()
    aws_prov = AWS()


def parse_args(args):
    parser = argparse.ArgumentParser(description="Test Deployment of instances")
    parser.add_argument("--p", "--provider", dest="provider", default="OpenStack",
                        help="Which provider to deploy the instance to")
    parser.add_argument("--s", "--scriptDeploy", dest="deploy_script", default=True, help='deploy script')
    return parser.parse_args(args)
