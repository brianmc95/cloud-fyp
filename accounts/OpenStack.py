from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from accounts.Account import Account


class OpenStackProvider(Account):

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
        node = self.driver.create_node(name=name,
                                       size=size,
                                       image=image,
                                       networks=networks,
                                       security_groups=security_groups)
        return node
