"""
    Brian McCarthy 114302146
    114302146@umail.ucc.ie
    brianmccarthy95@gmail.com

    Class to represent an Amazon EBS instance.
"""

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import json


class EBS_volume:
    """
        Class representing an EBS volume

        Attributes:
            Determine these
    """

    def __init__(self, size, name, region=None, location=None, snapshot=None, accessID_Local=".", accessKey_Local="."):
        self.size = size
        self.name = name
        self.region = region
        self.location = location
        self.snapshot = snapshot

        self.__accessID, self.__accessKey = self.__read_in_access_keys(accessID_Local, accessKey_Local)
        print(self.__accessID, self.__accessKey)

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

    def get_size(self):
        return self.size

    def get_name(self):
        return self.name

    def get_location(self):
        return self.location

    def get_snapshot(self):
        return self.snapshot

    def create_volume(self):
        locations = self.__driver.list_locations()
        location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        volume = self.__driver.create_volume(size=8, name="Test GP volume", ex_volume_type="gp2", location=location)
        self.__volume = volume
        print("Volume created")

    def delete_volume(self, volume_name):
        if volume_name == self.name:
            self.__driver.destroy_volume(self.__volume)
            del self

    def create_snapshot(self, volume_name):
        return self.__driver.create_volume_snapshot(self.__volume, volume_name)

    def attach_volume(self, node, volume_name, device="/dev/sdb"):
        if volume_name == self.name:
            success = self.__driver.attach_volume(node, self.__volume)
            if success:
                self.attached_nodes[node.get_name()] = node

    def detach_volume(self, node, volume_name):
        if volume_name == self.name:
            success = self.__driver.attach_volume(self.__volume)
            if success:
                self.attached_nodes.pop(node.get_name())

def main():
    myEBS = EBS_volume(8, "myEBS","eu-west-1",
                accessID_Local="/Users/BrianMcCarthy/amazonKeys/accessID",
                accessKey_Local="/Users/BrianMcCarthy/amazonKeys/sak2")
    myEBS.create_volume()

if __name__ == "__main__":
    main()

