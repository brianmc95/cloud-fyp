"""

    Brian McCarthy 114302146

    Class to represent an account for a user, this base class should not be instantiated, it's children will
    be used to define new access points to service providers. This also acts as an interface to the dashboard
    making it simpler by using this basic methods and not relying on having to implement them specifically.

"""


from libcloud.compute.base import NodeDriver
from pymongo import MongoClient
import random
import string


class Account:

    client = MongoClient('localhost', 27017)

    def __init__(self):
        self.driver = NodeDriver(key="SimpleBase")

    def list_images(self):
        return self.driver.list_images()

    def list_sizes(self):
        return self.driver.list_sizes()

    def list_key_pairs(self):
        return self.driver.list_key_pairs()

    def list_nodes(self):
        return self.driver.list_nodes()

    def list_volumes(self):
        return self.driver.list_volumes()

    def list_security_groups(self):
        raise NotImplementedError("This is not available in this interface")

    def list_networks(self):
        raise NotImplementedError("This is not available in this interface")

    def create_volume(self, name, size, location=None, snapshot=None):
        self.driver.create_volume(name=name, size=size, location=location, snapshot=snapshot)

    def attach_volume(self, node, volume):
        self.driver.attach_volume(node, volume)

    def dettach_volume(self, node, volume):
        node.detach_volume(volume)

    def destroy_volume(self, volume):
        self.driver.destroy_volume(volume)

    def create_node(self, *kwargs):
        raise NotImplementedError("This is not available in this interface")

    def destroy_node(self, node):
        self.destroy_node(node)

    def get_image(self, image_id):
        return self.driver.get_image(image_id)

    def get_size(self, size_id):
        return [s for s in self.driver.list_sizes() if s.id == size_id][0]

    def get_networks(self, net_ids):
        networks = []
        for net in self.list_networks():
            if net.id in net_ids:
                networks.append(net)
        return networks

    def get_security_groups(self, sec_ids):
        sec_groups = []
        for sec in self.list_security_groups():
            if sec.id in sec_ids:
                sec_groups.append(sec)
        return sec_groups

    def gen_id(self):
        attempt = 0
        inUse = 0
        while True:
            rand_id = "".join(random.choices(string.ascii_letters + string.digits, k=32))
            db = self.client["cloud-fyp"]
            collection = db["instances"]
            inUse = self.client.db.collection.count({'INSTANCE_ID': rand_id})
            attempt += 1
            if inUse < 0:
                break
            if attempt > 3:
                # TODO: Do something to deal with this.
                print("Failed to generate a random ID")
                break
        return rand_id


