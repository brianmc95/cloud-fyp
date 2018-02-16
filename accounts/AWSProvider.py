import libcloud.compute.types as node_types
import libcloud.compute.providers as node_providers
import libcloud.storage.types as storage_types
import libcloud.storage.providers as storage_providers

from accounts.Account import Account


class AWSProvider(Account):

    def __init__(self, region="eu-west-1", access_id_loc="/Users/BrianMcCarthy/amazonKeys/accessID",
                 access_key_loc="/Users/BrianMcCarthy/amazonKeys/sak2"):
        super().__init__()

        self.__access_id, self.__access_key = self.__read_in_access_keys(access_id_loc, access_key_loc)
        self.region = region
        self.ec2cls = node_providers.get_driver(node_types.Provider.EC2)
        self.s3cls = storage_providers.get_driver(storage_types.Provider.S3_EU_WEST)

        self.node_driver = self.ec2cls(self.__access_id, self.__access_key, region=self.region)
        self.storage_driver = self.s3cls(self.__access_id, self.__access_key, region=self.region)

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

    def create_node(self, name, size, image, networks, security_groups, key):
        node = self.node_driver.create_node(name=name,
                                            size=size,
                                            image=image,
                                            subnet=networks,
                                            ex_security_groups=security_groups,
                                            ex_keyname=key)
        return node

    def create_volume(self, name, size, device=None, location=None, avail_zone=None, snapshot=None):
        locations = self.node_driver.list_locations()
        if location is None:
            location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        else:
            location = [loc for loc in locations if loc.name == location][0]
        volume = self.node_driver.create_volume(name=name, size=size, location=location)
        return volume

    def create_container(self, container_name):
        container = self.storage_driver.create_container(container_name)
        return container

    def get_container(self, container_name):
        return self.storage_driver.get_container(container_name)

    def list_availability_zones(self):
        return self.node_driver.ex_list_availability_zones()

    def get_availability_zone(self, zone_name):
        for zone in self.node_driver.ex_list_availability_zones():
            if zone.name == zone_name:
                return zone

    def get_key_info(self):
        return self.__access_id, self.__access_key

