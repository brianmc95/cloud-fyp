import libcloud.compute.types as node_types
import libcloud.compute.providers as node_providers
import libcloud.storage.types as storage_types
import libcloud.storage.providers as storage_providers
import datetime
import paramiko
import time

from accounts.Account import Account
import json


class AWS(Account):

    def __init__(self, access_id="", secret_key="", region="", ):
        super().__init__()
        self.region = region
        self.ec2cls = node_providers.get_driver(node_types.Provider.EC2)
        self.s3cls = storage_providers.get_driver(storage_types.Provider.S3_EU_WEST)

        self.node_driver = self.ec2cls(access_id, secret_key, region=self.region)
        self.storage_driver = self.s3cls(access_id, secret_key, region=self.region)

        self.__free_tier_images = ["ami-075eca7e", "ami-b09e1ac9", "ami-32b6214b", "ami-c90195b0", "ami-8fd760f6",
                                   "ami-cddc5bb4", "ami-5bf34b22", "ami-70fe4609", "ami-8668d0ff", "ami-8c77cff5",
                                   "ami-5fd95e26", "ami-e79e1e9e", "ami-811a9ef8", "ami-d71793ae", "ami-9a8b0ce3",
                                   "ami-b3cb4cca", "ami-2e832957", "ami-0659cd7f", "ami-974cdbee"]

        self.__linux_mon = "linux_mon_diploy.sh"

    def list_images(self):
        images = []
        for imageID in self.__free_tier_images:
            images.append(self.node_driver.get_image(imageID))
        return images

    def list_networks(self):
        return self.node_driver.ex_list_subnets()

    def list_security_groups(self):
        return self.node_driver.ex_list_security_groups()

    def get_security_groups(self, sec_names):
        return sec_names

    def availability_zones(self):
        return self.node_driver.ex_list_availability_zones()

    def create_node(self, name, size, image, networks, security_groups, key_name):
        node = self.node_driver.create_node(name=name,
                                            size=size,
                                            image=image,
                                            subnet=networks,
                                            ex_security_groups=security_groups,
                                            ex_keyname=key_name)

        self.log_node(node, name, size, image, "aws")
        self.logger.info("Successfully added node to the instances db")
        key_loc = self.__get_key(key_name)
        self.deploy_monitor(node, key_loc, False)

    def __get_key(self, key_name):
        return "{}/{}/{}/{}.pem".format(self.root_path, "keys", "aws", key_name)

    def deploy_monitor(self, node, key_loc, log):
        if log:
            self.log_node(node, node.name, node.extra["instance_type"], node.extra["image_id"], "aws")

        start_time = datetime.datetime.now()
        current_time = datetime.datetime.now()
        ssh_names = ["ubuntu", "root", "ec2-user", "bitnami", "centos", "admin", "fedora"]
        current_pos = 0
        config_file = open("config/manager-config.json")
        config_json = json.load(config_file)
        ip = config_json["public-ip"]
        port = config_json["port"]
        git_install = False
        pip_install = False
        repo_clone = False
        script_run = False
        fails = 0
        while current_pos < len(ssh_names) and current_time - start_time < datetime.timedelta(
                minutes=8) and fails < 5 and not script_run:
            node = self.get_node(id=node.id)
            self.logger.info("FAILS: {}".format(fails))
            self.logger.info("GIT INSTALLED: {}".format(git_install))
            self.logger.info("PIP INSTALLED: {}".format(pip_install))
            self.logger.info("REPO CLONED: {}".format(repo_clone))
            self.logger.info("MONITORIN DEPLOYED: {}".format(script_run))
            if node.state == "running":
                try:
                    client = paramiko.SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    key = paramiko.RSAKey.from_private_key_file(key_loc)
                    self.logger.debug(node.public_ips[0])
                    self.logger.debug(ssh_names[current_pos])
                    self.logger.info("Setting up SSH session")
                    client.connect(node.public_ips[0], username=ssh_names[current_pos], pkey=key, timeout=180)
                    if not git_install:
                        self.logger.info("Preparing to install git")
                        transport = client.get_transport().open_session()
                        transport.exec_command("sudo apt install git -y")
                        if transport.recv_exit_status() > 1:
                            self.logger.info("Failed to install git")
                            fails += 1
                            continue
                        else:
                            self.logger.info("Git successfully installed")
                            git_install = True
                    if not pip_install and git_install:
                        self.logger.info("Preparing to install pip")
                        transport = client.get_transport().open_session()
                        transport.exec_command("sudo apt install python3-pip -y")
                        if transport.recv_exit_status() > 1:
                            self.logger.info("Failed to install Pip")
                            fails += 1
                            continue
                        else:
                            self.logger.info("Pip successfully installed")
                            pip_install = True
                    if not repo_clone and pip_install:
                        self.logger.info("Preparing to clone repo")
                        transport = client.get_transport().open_session()
                        self.logger.info("cloning repo")
                        transport.exec_command("git clone https://github.com/brianmc95/cloud-fyp.git")
                        if transport.recv_exit_status() > 1:
                            self.logger.ingo("Failed to clone repo")
                            fails += 1
                            continue
                        else:
                            self.logger.info("Repo successfully cloned")
                            repo_clone = True
                    if not script_run and repo_clone:
                        transport = client.get_transport().open_session()
                        self.logger.info("Deploying monitoring script")
                        transport.exec_command(
                            "/cloud-fyp/monitoring/utilities/linux_mon_deploy.sh -ip {} -p {} -id {} -pv {}".format(ip,
                                                                                                                    port,
                                                                                                                    node.id,
                                                                                                                    "aws"))
                        if transport.recv_exit_status() > 1:
                            self.logger.ingo("Failed to deploy script")
                            fails += 1
                            continue
                        else:
                            self.logger.info("Repo successfully deployed script")
                            script_run = True

                except paramiko.AuthenticationException as e:
                    self.logger.info(e)
                    self.logger.info("Incorrect username used trying another one.")
                    current_pos += 1
                    continue

                except paramiko.SSHException as e:
                    self.logger.info(e)
                    self.logger.info("Issue with ssh client failed to deploy")
                    break
            else:
                time.sleep(30)

    def create_volume(self, name, size, location=None, snapshot=None):
        if location is None:
            locations = self.node_driver.list_locations()
            location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        self.node_driver.create_volume(name=name, size=size, location=location)

    def create_container(self, container_name):
        container = self.storage_driver.create_container(container_name)
        return container

    def get_container(self, container_name):
        return self.storage_driver.get_container(container_name)

    def get_object(self, container_name, object_name):
        return self.storage_driver.get_object(container_name, object_name)

    def download_object_stream(self, obj):
        return self.storage_driver.download_object_as_stream(obj)

    def list_availability_zones(self):
        return self.node_driver.ex_list_availability_zones()

    def get_availability_zone(self, zone_name):
        for zone in self.node_driver.ex_list_availability_zones():
            if zone.name == zone_name:
                return zone
