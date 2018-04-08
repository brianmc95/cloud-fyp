from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from keystoneauth1 import loading
from keystoneauth1 import session
from glanceclient import Client
import paramiko
import datetime
import time

from accounts.Account import Account
import json


class OpenStack(Account):

    def __init__(self, access_name, password, auth_url, auth_version, tenant_name, project_id, glance_version):
        super().__init__()
        OpenStack = get_driver(Provider.OPENSTACK)
        self.node_driver = OpenStack(access_name, password,
                                     ex_force_auth_url=auth_url,
                                     ex_force_auth_version=auth_version,
                                     ex_tenant_name=tenant_name)
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url=auth_url,
            username=access_name,
            password=password,
            project_id=project_id)
        sesh = session.Session(auth=auth)
        self.glance = Client(glance_version, session=sesh)

        # TODO: deal with glance version Migration service.

    def list_networks(self):
        return self.node_driver.ex_list_networks()

    def list_security_groups(self):
        return self.node_driver.ex_list_security_groups()

    def create_node(self, name, size, image, networks, security_groups, key_name):
        node = self.node_driver.create_node(name=name,
                                            size=size,
                                            image=image,
                                            subnet=networks,
                                            ex_security_groups=security_groups,
                                            ex_keyname=key_name)

        self.log_node(node, name, size, image, "openstack")
        self.logger.info("Successfully added node to the instances db")
        key_loc = self.__get_key(key_name)
        result = self.deploy_monitor(node, key_loc, False)
        return result

    def __get_key(self, key_name):
        return "{}/{}/{}/{}.pem".format(self.root_path, "keys", "openstack", key_name)

    def deploy_monitor(self, node, key_loc, log):
        if log:
            self.log_node(node, node.name, node.extra["instance_type"], node.extra["image_id"], "openstack")

        start_time = datetime.datetime.now()
        current_time = datetime.datetime.now()
        ssh_names = ["ubuntu", "root", "ec2-user", "bitnami", "centos", "admin", "fedora"]
        current_pos = 0
        config_file = open("config/manager-config.json")
        config_json = json.load(config_file)
        ip = config_json["public-ip"]
        port = config_json["port"]
        apt_get_update = False
        git_install = False
        pip_install = False
        repo_clone = False
        script_run = False
        fails = 0
        while current_pos < len(ssh_names) and current_time - start_time < datetime.timedelta(minutes=10) and fails < 5:
            node = self.get_node(id=node.id)
            self.logger.info("FAILS: {}".format(fails))
            self.logger.info("APT-GET UPDATE: {}".format(apt_get_update))
            self.logger.info("GIT INSTALLED: {}".format(git_install))
            self.logger.info("PIP INSTALLED: {}".format(pip_install))
            self.logger.info("REPO CLONED: {}".format(repo_clone))
            self.logger.info("MONITORING DEPLOYED: {}".format(script_run))
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

                    if not apt_get_update:
                        self.logger.info("Update apt-get to ensure it works correctly.")
                        transport = client.get_transport().open_session()
                        transport.exec_command("sudo apt-get update -y")
                        if transport.recv_exit_status() > 1:
                            self.logger.info("Failed to update apt-get")
                            fails += 1
                            continue
                        else:
                            self.logger.info("apt-get updated successfully")
                            apt_get_update = True

                    if not git_install and apt_get_update:
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
                        self.logger.info("Preparing to install python3-pip")
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
                            self.logger.info("Failed to clone repo")
                            fails += 1
                            continue
                        else:
                            self.logger.info("Repo successfully cloned")
                            repo_clone = True

                    if not script_run and repo_clone:
                        transport = client.get_transport().open_session()
                        self.logger.info("Deploying monitoring script")
                        transport.exec_command(
                            "./cloud-fyp/monitoring/utilities/linux_mon_deploy.sh -ip {} -p {} -id {} -pv {}".format(ip,
                                                                                                                    port,
                                                                                                                    node.id,
                                                                                                                    "aws"))
                        if transport.recv_exit_status() > 1:
                            self.logger.info("Failed to deploy script")
                            fails += 1
                            continue
                        else:
                            self.logger.info("Successfully deployed script")
                            return True

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

    def get_node_info(self, node_id):
        return self.node_driver.ex_get_node_details(node_id)

    def create_image(self, image_name, container_format, disk_format, image_location):
        image = self.glance.images.create(name=image_name, container_format=container_format, disk_format=disk_format)
        self.glance.images.update(image, copy_from=image_location)
