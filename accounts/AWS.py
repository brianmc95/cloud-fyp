from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment, ScriptDeployment

from accounts.Account import Account
import json


class AWS(Account):

    def __init__(self, access_id="", secret_key="", region="",):
        super().__init__()
        self.region = region
        self.cls = get_driver(Provider.EC2)
        self.driver = self.cls(access_id, secret_key, region=self.region)

        self.__free_tier_images = ["ami-075eca7e", "ami-b09e1ac9", "ami-32b6214b", "ami-c90195b0", "ami-8fd760f6",
                                   "ami-cddc5bb4", "ami-5bf34b22", "ami-70fe4609", "ami-8668d0ff", "ami-8c77cff5",
                                   "ami-5fd95e26", "ami-e79e1e9e", "ami-811a9ef8", "ami-d71793ae", "ami-9a8b0ce3",
                                   "ami-b3cb4cca", "ami-2e832957", "ami-0659cd7f", "ami-974cdbee"]

        self.__linux_mon = "linux_mon_diploy.sh"

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

        if mon:
            self.log_node(node, node_id, name, size, image, "AWS")

    def create_volume(self, name, size, location=None, snapshot=None):
        if location is None:
            locations = self.driver.list_locations()
            location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        self.driver.create_volume(name=name, size=size, location=location)
