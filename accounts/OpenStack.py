from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment, ScriptDeployment
from libcloud.compute.base import DeploymentError
from libcloud.compute.base import NodeAuthSSHKey
from keystoneauth1 import loading
from keystoneauth1 import session
from glanceclient import Client

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
        # Instantiate the Nova instance.
        node = self.node_driver.create_node(name=name,
                                            size=size,
                                            image=image,
                                            networks=networks,
                                            security_groups=security_groups,
                                            ex_keyname=key_name)
        return node

    def get_node_info(self, node_id):
        return self.node_driver.ex_get_node_details(node_id)

    def deploy_node_script(self, name, size, image, networks, security_groups, mon, key_loc, script=None):
        try:
            self.logger.info("Beginning the deployment of the instance")
            self.logger.info("name {}, size {}, image {}, networks {}, security_groups {}, mon {}, key_loc {}")
            steps = []
            if mon:
                config_file = open("config/manager-config.json")
                config_json = json.load(config_file)
                node_id = self.gen_id()
                ip = config_json["public-ip"]
                port = config_json["port"]
                mon_args = ["-ip {}".format(ip), "-p {}".format(port), "-id {}".format(node_id), "-n {}".format(name)]
                self.logger.info("node_id: {} IP: {}, PORT: {} args: {}".format(node_id, ip, port, mon_args))
                steps.append(ScriptDeployment(self.linux_mon, args=mon_args))
            if script:
                steps.append(ScriptDeployment(script))

            key_file = open(key_loc)
            key = NodeAuthSSHKey(key_file.read())
            key_name = key_loc.split("/")[-1]
            key_name = key_name.split(".")[0]
            msd = MultiStepDeployment([key, steps])

            self.logger.debug("Key name associated with node".format(key_name))

            node = self.node_driver.deploy_node(name=name,
                                                size=size,
                                                image=image,
                                                networks=networks,
                                                ex_security_groups=security_groups,
                                                auth=key,
                                                ssh_key=key_loc,
                                                ex_keyname=key_name,
                                                deploy=msd,
                                                timeout=180)

            if mon:
                self.log_node(node, node_id, name, size, image, "OPENSTACK")
                self.logger.info("Successfully added node to the instances db")

            return True
        except DeploymentError as e:
            self.logger.exception("Deployment failed could not connect to node, timeout error")
            self.logger.exception(e)
            return False
        except IOError as e:
            self.logger.exception("Key file was unnaccessible and so failed to deploy node")
            return False
        except json.JSONDecodeError as e:
            self.logger.exception("Was unable to open json config file")
            self.logger.exception(e)
            return False

    def create_image(self, image_name, container_format, disk_format, image_location):
        image = self.glance.images.create(name=image_name, container_format=container_format, disk_format=disk_format)
        self.glance.images.update(image, copy_from=image_location)
