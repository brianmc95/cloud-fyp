"""
Class representing the OpenStack Nova instance

Brian McCarthy 114302146
brianmccarthy95@gmail.com
114302146@umail.ucc.ie
"""

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider


class Nova:

    def __init__(self):
        # This obviously needs changing but that will be dealt with later.
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

    def getImages(self):
        return self.__images

    def getSizes(self):
        return self.__sizes

    def setImage(self, image):
        self.__nodeImage = image

    def setSize(self, size):
        self.__nodeSize = size

    def instantiate_nova(self):
        # Instantiate the EC2 instance.
        self.__driver.create_node(name="first-auto-deploy",
                                  image=self.__nodeImage,
                                  size=self.__nodeSize,
                                  networks=self.network,
                                  ex_security_groups=self.securityGroups,
                                  ex_keyname="vscaler-keypair")
def main():
    newNova = Nova()
    newNova.setImage()
    newNova.instantiate_nova()

if __name__ == "__main__":
    main()



