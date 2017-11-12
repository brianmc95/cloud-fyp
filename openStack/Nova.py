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
        passFile = open("/Users/BrianMcCarthy/vscalerKeys/pass")
        password = passFile.read().strip()

        OpenStack = get_driver(Provider.OPENSTACK)
        self.__driver = OpenStack("bmcc", password,
                           ex_force_auth_url='http://identity.api.vscaler.com:5000',
                           ex_force_auth_version='2.0_password',
                           ex_tenant_name='bmcc')

        images = self.__driver.list_images()
        sizes = self.__driver.list_sizes()

        for image in images:
            if "Ubuntu" in image.name:
                self.__nodeImage = image
                break

        for size in sizes:
            if size.name == "m1.small":
                self.__nodeSize = size
                break

    def instantiate_nova(self):
        # Instantiate the EC2 instance.
        self.__driver.create_node(name="first-auto-deploy", image=self.__nodeImage, size=self.__nodeSize)
        print("Nova successfully deployed")


def main():
    newNova = Nova()
    newNova.instantiate_nova()


if __name__ == "__main__":
    main()





