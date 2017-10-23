"""
    Brian McCarthy 114302146
    114302146@umail.ucc.ie
    brianmccarthy95@gmail.com

    Class to represent an Amazon EBS instance.
"""

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class EBS_volume:
    """
        Class representing an EBS volume

        Attributes:
            Determine these
    """

    def __init__(self, name, size, ebs_type="gp2", region=None,
                 location=None, snapshot=None, delete_on_terminate=True,
                 accessID_Local=".", accessKey_Local="."):
        self.name = name
        self.size = size
        self.ebs_type = ebs_type
        self.region = region
        self.location = location
        self.snapshot = snapshot
        self.delete_on_terminate = delete_on_terminate


        self.__accessID, self.__accessKey = self.__read_in_access_keys(accessID_Local, accessKey_Local)

        self.__cls = get_driver(Provider.EC2)
        self.__driver = self.__cls(self.__accessID, self.__accessKey, region=self.region)

        self.attached_nodes = {}
        self.__volume = None


    def __read_in_access_keys(self, accessIDLocal, accessKeyLocal):
        accessID_file = open(accessIDLocal, "r")
        accessKey_file = open(accessKeyLocal, "r")
        accessID = accessID_file.readline().strip()
        accessKey = accessKey_file.readline().strip()
        return accessID, accessKey

    def __str__(self):
        return "< %s , %s , %s >" % (self.size, self.name, self.region)

    def __del__(self):
        return "Volume %s: destroyed" % (self.name)

    def set_size(self, size):
        self.size = size

    def set_name(self, name):
        self.name = name

    def set_location(self, location):
        self.location = location

    def set_snapshot(self, snapshot):
        self.snapshot = snapshot

    def add_node(self, node):
        self.attached_nodes[node.get_name()] = node

    def get_size(self):
        return self.size

    def get_name(self):
        return self.name

    def get_location(self):
        return self.location

    def get_snapshot(self):
        return self.snapshot

    def get_attached_nodes(self):
        return self.attached_nodes

    def create_volume(self):
        locations = self.__driver.list_locations()
        location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        volume = self.__driver.create_volume(size=self.size, name=self.name,
                                             ex_volume_type=self.ebs_type, location=location)
        self.__volume = volume

    def get_block_device_mapping(self):
        return {"DeviceName": self.name,
                "Ebs": {
                    "DeleteOnTermination": self.delete_on_terminate,
                    "SnapshotId": self.snapshot,
                    "VolumeSize": self.size,
                    "VolumeType": self.ebs_type}}

    # --------------------------------------------------------------------------- #
    # For the time being these methods don't apply

    def delete_volume(self, volume_name):
        if volume_name == self.name:
            self.__driver.destroy_volume(self.__volume)
            del self

    def create_snapshot(self, volume_name):
        return self.__driver.create_volume_snapshot(self.__volume, volume_name)

    def attach_volume(self, node):
        success = self.__driver.attach_volume(node, self.__volume)
        if success:
            self.attached_nodes[node.get_name()] = node
            node.add_associated_ebs_volume(self.__volume)

    def detach_volume(self, node):
        success = self.__driver.dettach_volume(self.__volume)
        if success:
            self.attached_nodes.pop(node.get_name())

def main():
    myEBS = EBS_volume(8, "myEBS", "eu-west-1",
                accessID_Local="/Users/BrianMcCarthy/amazonKeys/accessID",
                accessKey_Local="/Users/BrianMcCarthy/amazonKeys/sak2")
    myEBS.create_volume()

if __name__ == "__main__":
    main()

