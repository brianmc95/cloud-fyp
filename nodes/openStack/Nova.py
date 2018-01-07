"""
Class representing the OpenStack Nova instance

Brian McCarthy 114302146
brianmccarthy95@gmail.com
114302146@umail.ucc.ie
"""

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

from nodes import node


class Nova(node.Node):

    def __init__(self, name, keyPair):
        # This obviously needs changing but that will be dealt with later.
        super().__init__(name, keyPair)
        passFile = open("/Users/BrianMcCarthy/vscalerKeys/pass")
        password = passFile.read().strip()

        OpenStack = get_driver(Provider.OPENSTACK)
        self.__driver = OpenStack("bmcc", password,
                               ex_force_auth_url='http://identity.api.vscaler.com:5000',
                               ex_force_auth_version='2.0_password',
                               ex_tenant_name='bmcc')

        self.__images = self.__driver.list_images()
        self.__sizes = self.__driver.list_sizes()

        self.networks = self.__driver.ex_list_networks()
        self.network = [self.networks[2]]
        self.securityGroups = self.__driver.ex_list_security_groups()

    def get_images(self):
        return self.__images

    def get_sizes(self):
        return self.__sizes

    def set_image(self, imageID):
        for image in self.__images:
            if image.id == imageID:
                self.image = image

    def set_size(self, sizeID):
        for size in self.__sizes:
            if size.id == sizeID:
                self.size = size

    def instantiate_node(self):
        # Instantiate the Nova instance
        self.__driver.create_node(name=self.name,
                                  image=self.image,
                                  size=self.size,
                                  networks=self.networks)


def main():
    nova = Nova("test", "don't care")


if __name__ == "__main__":
    main()





