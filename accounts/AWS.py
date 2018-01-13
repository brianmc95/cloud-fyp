from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from accounts.Account import Account


class AWS(Account):

    def __init__(self, region="eu-west-1", access_id_loc="/Users/BrianMcCarthy/amazonKeys/accessID",
                 access_key_loc="/Users/BrianMcCarthy/amazonKeys/sak2"):
        super().__init__()

        access_id, access_key = self.__read_in_access_keys(access_id_loc, access_key_loc)
        self.region = region
        self.cls = get_driver(Provider.EC2)
        self.driver = self.cls(access_id, access_key, region=self.region)

        self.__free_tier_images = ["ami-075eca7e", "ami-b09e1ac9", "ami-32b6214b", "ami-c90195b0", "ami-8fd760f6",
                                   "ami-cddc5bb4", "ami-5bf34b22", "ami-70fe4609", "ami-8668d0ff", "ami-8c77cff5",
                                   "ami-5fd95e26", "ami-e79e1e9e", "ami-811a9ef8", "ami-d71793ae", "ami-9a8b0ce3",
                                   "ami-b3cb4cca", "ami-2e832957", "ami-0659cd7f", "ami-974cdbee"]

    def __read_in_access_keys(self, access_id_loc, access_key_loc):
        access_id_file = open(access_id_loc, "r")
        access_key_file = open(access_key_loc, "r")
        access_id = access_id_file.readline().strip()
        access_key = access_key_file.readline().strip()
        return access_id, access_key

    def list_images(self):
        images = []
        for imageID in self.__free_tier_images:
            images.append(self.driver.get_image(imageID))
        return images

    def list_networks(self):
        return self.driver.ex_list_subnets()

    def list_security_groups(self):
        return self.driver.ex_list_security_groups()

    def get_security_groups(self, sec_names):
        return sec_names

    def availability_zones(self):
        return self.driver.ex_list_availability_zones()

    def create_node(self, name, size, image, networks, security_groups):
        self.driver.create_node(name=name,
                                size=size,
                                image=image,
                                subnet=networks,
                                security_groups=security_groups)

    def create_volume(self, name, size, location=None, snapshot=None):
        if location is None:
            locations = self.driver.list_locations()
            location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        self.driver.create_volume(name=name, size=size, location=location)
