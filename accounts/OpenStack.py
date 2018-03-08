from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment, ScriptDeployment

from accounts.Account import Account
import json


class OpenStackProvider(Account):

    __linux_mon = "linux_mon_diploy.sh"

    def __init__(self):
        super().__init__()
        passFile = open("/Users/BrianMcCarthy/vscalerKeys/pass")
        password = passFile.read().strip()

        OpenStack = get_driver(Provider.OPENSTACK)
        self.driver = OpenStack("bmcc", password,
                                ex_force_auth_url='http://identity.api.vscaler.com:5000',
                                ex_force_auth_version='2.0_password',
                                ex_tenant_name='bmcc')

    def list_networks(self):
        return self.driver.ex_list_networks()

    def list_security_groups(self):
        return self.driver.ex_list_security_groups()

    def create_node(self, name, size, image, networks, security_groups):
        # Instantiate the Nova instance.
        self.driver.create_node(name=name,
                                size=size,
                                image=image,
                                networks=networks,
                                security_groups=security_groups)

    def deploy_node_script(self, name, size, image, networks, security_groups, mon, script=None):
        steps = []
        if mon:
            config_file = open("config/manager-config.json")
            config_json = json.load(config_file)
            node_id = self.gen_id()
            ip = config_json["ip"]
            port = config_json["port"]
            mon_args = ["-ip {}".format(ip), "-p {}".format(port), "-id {}".format(node_id), "-n {}".format(name)]
            steps.append(ScriptDeployment(self.__linux_mon, args=mon_args))
        if script:
            steps.append(ScriptDeployment(script))

        msd = MultiStepDeployment(steps)

        node = self.driver.deploy_node(name=name,
                                       size=size,
                                       image=image,
                                       networks=networks,
                                       security_groups=security_groups,
                                       deploy=msd)
