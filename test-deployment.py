# !/usr/bin/env python3.6

from accounts.OpenStack import OpenStackProvider
from accounts.AWS import AWS
import argparse


def test_deployment(provider, script_deploy, operating_system):
    if provider == "OpenStack":
        provider = OpenStackProvider()
        if operating_system == "ubuntu":
            ubuntu_image = provider.get_image("48c5d226-7aec-4357-b505-1d8c9bd0a03b")
        elif operating_system == "windows":
            windows_image = provider.get_image("8ecba049-1a02-425a-9ed2-a282fda66d26")
        node_size = provider.get_size("3")
        node_net = provider.get_networks("20a073e3-3b87-4717-bca3-ea3c5edbe470")
        node_sec = provider.get_security_groups("ccbf6422-d7b0-4dfb-8ca6-9475b5558bd0")
    elif provider == "AWS":
        provider = AWS()
        if operating_system == "ubuntu":
            ubuntu_image = provider.get_image("ami-8fd760f6")
        elif operating_system == "windows":
            windows_image = provider.get_image("ami-b3cb4cca")
        node_size = provider.get_size("t1.micro")
        node_net = provider.get_networks("subnet-82cb7ed9")
        node_sec = provider.get_security_groups("launch-wizard-4")

    if script_deploy:
        print("Deploy with script")
    else:
        print("Deploy without script")


def main():
    parser = argparse.ArgumentParser(description="Test Deployment of instances")
    parser.add_argument("-p", "--provider", dest="provider", default="OpenStack",
                        help="Which provider to deploy the instance to")
    parser.add_argument("-s", "--scriptDeploy", dest="deploy_script", default=True, help='deploy script')
    parser.add_argument("-o", "--operatingSystem", dest="os", default="ubuntu", help="os to deploy node with")


if __name__ == "__main__":
    main()
