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

    def __init__(self, size, name, region=None, location=None, snapshot=None):
        self.size = size
        self.name = name
        self.region = region
        self.location = location
        self.snapshot = snapshot

        self._cls = get_driver(Provider.EC2)
        self._driver = self._cls("To be filled in", "To be filled in", region=self.region)

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
        locations = self._driver.list_locations()
        location = [r for r in locations if r.availability_zone.region_name == self.region][0]
        print(location)
        volume = self._driver.create_volume(size=8, name="Test GP volume", ex_volume_type="gp2", location=location)
