from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment, ScriptDeployment
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
        steps = []
        if mon:
            config_file = open("config/manager-config.json")
            config_json = json.load(config_file)
            node_id = self.gen_id()
            ip = config_json["public-ip"]
            port = config_json["port"]
            mon_args = ["-ip {}".format(ip), "-p {}".format(port), "-id {}".format(node_id), "-n {}".format(name)]
            steps.append(ScriptDeployment(self.linux_mon, args=mon_args))
        if script:
            steps.append(ScriptDeployment(script))

        msd = MultiStepDeployment(steps)

        node = self.node_driver.deploy_node(name=name,
                                            size=size,
                                            image=image,
                                            networks=networks,
                                            security_groups=security_groups,
                                            ssh_key=key_loc,
                                            deploy=msd)

        if mon:
            self.log_node(node, node_id, name, size, image, "OPENSTACK")

    def create_image(self, image_name, container_format, disk_format, image_location):
        image = self.glance.images.create(name=image_name, container_format=container_format, disk_format=disk_format)
        self.glance.images.update(image, copy_from=image_location)
