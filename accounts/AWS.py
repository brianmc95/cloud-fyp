import libcloud.compute.types as node_types
import libcloud.compute.providers as node_providers
import libcloud.storage.types as storage_types
import libcloud.storage.providers as storage_providers
from libcloud.compute.deployment import MultiStepDeployment, ScriptDeployment

from accounts.Account import Account
import json


class AWS(Account):

    def __init__(self, access_id="", secret_key="", region="",):
        super().__init__()
        self.region = region
        self.ec2cls = node_providers.get_driver(node_types.Provider.EC2)
        self.s3cls = storage_providers.get_driver(storage_types.Provider.S3_EU_WEST)

        self.node_driver = self.ec2cls(access_id, secret_key, region=self.region)
        self.storage_driver = self.s3cls(access_id, secret_key, region=self.region)

        self.__free_tier_images = ["ami-075eca7e", "ami-b09e1ac9", "ami-32b6214b", "ami-c90195b0", "ami-8fd760f6",
                                   "ami-cddc5bb4", "ami-5bf34b22", "ami-70fe4609", "ami-8668d0ff", "ami-8c77cff5",
                                   "ami-5fd95e26", "ami-e79e1e9e", "ami-811a9ef8", "ami-d71793ae", "ami-9a8b0ce3",
                                   "ami-b3cb4cca", "ami-2e832957", "ami-0659cd7f", "ami-974cdbee"]

        self.__linux_mon = "linux_mon_diploy.sh"

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

    def create_node(self, name, size, image, networks, security_groups):
        self.node_driver.create_node(name=name,
                                size=size,
                                image=image,
                                subnet=networks,
                                security_groups=security_groups)

    def deploy_node_script(self, name, size, image, networks, security_groups, mon, script=None):
        steps = []
        if mon:
            config_file = open("config/manager-config.json")
            config_json = json.load(config_file)
            node_id = self.gen_id()
            ip = config_json["public-ip"]
            port = config_json["port"]
            mon_args = ["-ip {}".format(ip), "-p {}".format(port), "-id {}".format(node_id), "-n {}".format(name)]
            steps.append(ScriptDeployment(self.__linux_mon, args=mon_args))
        if script:
            steps.append(ScriptDeployment(script))

        msd = MultiStepDeployment(steps)

        node = self.node_driver.deploy_node(name=name,
                                       size=size,
                                       image=image,
                                       networks=networks,
                                       security_groups=security_groups,
                                       deploy=msd)

        if mon:
            self.log_node(node, node_id, name, size, image, "AWS")

    def create_volume(self, name, size, location=None, snapshot=None):
        if location is None:
            locations = self.node_driver.list_locations()
            location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        self.node_driver.create_volume(name=name, size=size, location=location)

    def create_container(self, container_name):
        container = self.storage_driver.create_container(container_name)
        return container

    def get_container(self, container_name):
        return self.storage_driver.get_container(container_name)

    def get_object(self, container_name, object_name):
        return self.storage_driver.get_object(container_name, object_name)

    def download_object_stream(self, obj):
        return self.storage_driver.download_object_as_stream(obj)

    def list_availability_zones(self):
        return self.node_driver.ex_list_availability_zones()

    def get_availability_zone(self, zone_name):
        for zone in self.node_driver.ex_list_availability_zones():
            if zone.name == zone_name:
                return zone

