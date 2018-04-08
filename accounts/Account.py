"""
    Brian McCarthy 114302146

    Class to represent an account for a user, this base class should not be instantiated, it's children will
    be used to define new access points to service providers. This also acts as an interface to the dashboard
    making it simpler by using this basic methods and not relying on having to implement them specifically.
"""


from libcloud.compute.base import NodeDriver
from libcloud.storage.base import StorageDriver
from pymongo import MongoClient
import pymongo.errors
import datetime
import os
import random
from retrying import retry
import logging


class Account:

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.node_driver = NodeDriver(key="SimpleBase")
        self.storage_driver = StorageDriver(key="SimpleBase")
        self.client = MongoClient('localhost', 27017)
        self.db = self.client["cloud-fyp"]
        self.inst_info = self.db["instances"]
        self.vols = self.db["volumes"]
        self.root_path = self.__get_root_path()
        self.linux_mon = "{}/monitoring/utilities/linux_mon_diploy.sh".format(self.root_path)

    def __get_root_path(self):
        full_path = os.getcwd()
        root_path = ""
        for directory in full_path.split('/'):
            if directory == "cloud-fyp":
                root_path += directory
                return root_path
            root_path += "{}/".format(directory)

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

    def detach_volume(self, volume):
        return self.node_driver.detach_volume(volume)

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
        return self.storage_driver.create_container(container_name)

    def upload_to_container(self, path, container, object_name):
        self.storage_driver.upload_object(file_path=path, container=container, object_name=object_name)

    def download_from_container(self, container, file_name, dest):
        obj = self.storage_driver.get_object(container.name, object_name=file_name)
        return obj.download(destination_path=dest)

    def delete_object(self):
        return NotImplementedError

    def list_containers(self):
        return self.storage_driver.list_containers()

    def get_node(self, name=None, id=None):
        for node in self.node_driver.list_nodes():
            if (node.id == id or node.name == name) and node.state.lower() != "terminated":
                return node


    def log_node(self, node, name, size, image, provider):
        post = {
            "INSTANCE_ID": node.id,
            "INSTANCE_NAME": name,
            "SIZE": size.name,
            "IMAGE": image.name,
            "PROVIDER": provider,
            "CREATION": datetime.datetime.now()
        }
        try:
            self.inst_info.insert_one(post)
        except pymongo.errors.PyMongoError as e:
            print(e)
            print("Issue when posting node info")
