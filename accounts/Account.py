"""
    Brian McCarthy 114302146

    Class to represent an account for a user, this base class should not be instantiated, it's children will
    be used to define new access points to service providers. This also acts as an interface to the dashboard
    making it simpler by using this basic methods and not relying on having to implement them specifically.
"""


from libcloud.compute.base import NodeDriver
from libcloud.container.base import ContainerDriver

import random
from retrying import retry


class Account:

    def __init__(self):
        self.node_driver = NodeDriver(key="SimpleBase")
        self.container_driver = ContainerDriver(key="SimpleBase")

    def list_images(self):
        return self.node_driver.list_images()

    def list_sizes(self):
        return self.node_driver.list_sizes()

    def list_key_pairs(self):
        return self.node_driver.list_key_pairs()

    def list_nodes(self):
        return self.node_driver.list_nodes()

    def list_volumes(self):
        return self.node_driver.list_volumes()

    def list_security_groups(self):
        raise NotImplementedError("This is not available in this interface")

    def list_networks(self):
        raise NotImplementedError("This is not available in this interface")

    def create_volume(self, name, size, location=None, snapshot=None):
        volume = self.node_driver.create_volume(name=name, size=size, location=location, snapshot=snapshot)
        return volume

    @retry(stop_max_delay=20000, wait_fixed=2000)
    def attach_volume(self, node, volume, device=None):
        if device is None:
            device = "/dev/sd" + "".join(random.choice("fghijklmnop"))
        return self.node_driver.attach_volume(node, volume, device)

    def dettach_volume(self, node, volume):
        node.detach_volume(volume)

    def destroy_volume(self, volume):
        self.node_driver.destroy_volume(volume)

    def create_node(self, *kwargs):
        raise NotImplementedError("This is not available in this interface")

    def destroy_node(self, node):
        self.node_driver.destroy_node(node)

    def get_image(self, image_id):
        return self.node_driver.get_image(image_id)

    def get_size(self, size_id):
        return [s for s in self.node_driver.list_sizes() if s.id == size_id][0]

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

    def get_volume(self, vol_id):
        for vol in self.list_volumes():
            if vol.id == vol_id:
                return vol

    def create_container(self, container_name):
        print(self.container_driver.list_images())
        # self.container_driver.deploy_container()

    def list_containers(self):
        return self.container_driver.list_containers()

    def get_node(self, name=None, id=None):
        for node in self.node_driver.list_nodes():
            if node.id == id or node.name == name:
                return node



