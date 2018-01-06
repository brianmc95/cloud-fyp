"""
    Brian McCarthy 114302146
    114302146@umail.ucc.ie
    brianmccarthy95@gmail.com

    Class to represent an Amazon EC2 instance.
"""

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage
from aws.EBS_volume import EBS_volume


class EC2:
    """
        Class representing an EC2 instance type

        Attributes:
            Determine these
    """

    # Free tier AMI -> "ami-acd005d5"
    # Free tier proc size -> "t2.micro"
    # My Region -> "eu-west-1"
    # My keyPair -> "firstTestInstance"
    # Need means of accessing public AWS key and private AWS key. But these shouldn't be stored here. in a user class

    def __init__(self, user, name, imageID, size, region, keyname,
                 userdata=None, security_groups=[], mincount=1, maxcount=1,
                 ebs_optimized=True, accessID_Local=".", accessKey_Local="."):
        # Initial setup of EC2 instance.
        self.user = user
        self.name = name
        self.imageID = imageID
        self.size = size
        self.region = region
        self.keyname = keyname
        self.userdata = userdata
        self.security_groups = security_groups
        self.mincount = mincount
        self.maxcount = maxcount
        self.ebs_optimized = ebs_optimized

        self.EBS_volumes = {}

        self.__accessID, self.__accessKey = self.__read_in_access_keys(accessID_Local, accessKey_Local)

        self.__cls = get_driver(Provider.EC2)
        self.__driver = self.__cls(self.__accessID, self.__accessKey, region=self.region)

        self.__free_tier_images = ["ami-075eca7e", "ami-b09e1ac9", "ami-32b6214b", "ami-c90195b0", "ami-8fd760f6",
                                   "ami-cddc5bb4", "ami-5bf34b22", "ami-70fe4609", "ami-8668d0ff", "ami-8c77cff5",
                                   "ami-5fd95e26", "ami-e79e1e9e", "ami-811a9ef8", "ami-d71793ae", "ami-9a8b0ce3",
                                   "ami-b3cb4cca", "ami-2e832957", "ami-0659cd7f", "ami-974cdbee"]

    def __str_(self):
        return "%s: %s, %s, %s, %s" % (self.name, self.imageID, self.region,
                                       self.EBS_volumes, self.keyname)

    def __read_in_access_keys(self, accessIDLocal, accessKeyLocal):
        accessID_file = open(accessIDLocal, "r")
        accessKey_file = open(accessKeyLocal, "r")
        accessID = accessID_file.readline().strip()
        accessKey = accessKey_file.readline().strip()
        return accessID, accessKey

    def set_user(self, user):
        # User object gives access to necessary account details.
        self.user = user

    def set_name(self, name):
        # Set the name of the EC2 instance
        self.name = name

    def set_imageID(self, imageID):
        # ID of the image type instantiated with this EC2.
        self.imageID = imageID

    def set_size(self, size):
        # Size is the size of the EC2 you want. i.e. processing size
        self.size = size

    def set_region(self, region):
        # Region in which this EC2 instance is instantiated
        self.region = region

    def set_keyname(self, keyname):
        # Key Pair used to access this EC2 instance
        self.keyname = keyname

    def set_security_groups(self, security_groups):
        # Security group(s) this instance is associated with
        self.security_groups = security_groups

    def set_mincount(self, mincount):
        # Minimum number of this EC2 image to instantiate
        self.mincount = mincount

    def set_maxcount(self, maxcount):
        # Maximum number of this EC2 image to instantiate
        self.maxcount = maxcount

    def set_ebs_optimized(self, ebs_optimized):
        # Boolean representing if this EC2 is optimized for EBS
        self.ebs_optimized = ebs_optimized

    def set_ip_addr(self, ip_addr):
        # Setter to get the IP address of the EC2 instance
        self.ip_addr = ip_addr

    def add_associated_ebs_volume(self, volume):
        # EBS volumes associated with this EC2 instance.
        self.EBS_volumes[volume.get_name()] = volume

    def remove_associated_ebs_volume(self, volumeName):
        # Remove a volume associated with this EC2 instance
        if volumeName in self.EBS_volumes:
            ebs = self.EBS_volumes[volumeName]
            ebs.dettach_volume(self, volumeName)
            self.EBS_volumes.pop(volumeName)

    def get_user(self):
        # Return the user associated with this EC2 instance
        return self.user

    def get_name(self):
        # Return the name of the EC2 instance
        return self.name

    def get_imageID(self):
        # return ID of the image type instantiated with this EC2.
        return self.imageID

    def get_size(self):
        # return size of the EC2 instance
        return self.size

    def get_region(self):
        # return Region in which this EC2 instance is instantiated
        return self.region

    def get_keyname(self):
        # return name of Key Pair used to access this EC2 instance
        return self.keyname

    def get_security_groups(self):
        # return Security group(s) this instance is associated with
        return self.security_groups

    def get_mincount(self):
        # return Minimum number of this EC2 image to instantiate
        return self.mincount

    def get_maxcount(self):
        # return Maximum number of this EC2 image to instantiate
        return self.maxcount

    def get_associated_ebs_volumes(self):
        # return EBS volumes associated with this EC2 instance.
        return self.EBS_volumes

    def get_ebs_optimized(self):
        # return Boolean representing if this EC2 is optimized for EBS
        return self.ebs_optimized

    def get_ip_addr(self):
        # Return the IP address of this instance
        return self.ip_addr

    def instantiate_ec2(self, ebs):
        # Instantiate the EC2 instance.
        sizes = self.__driver.list_sizes(self.region)
        size = [s for s in sizes if s.id == self.size][0]
        image = NodeImage(id=self.imageID, name=self.name, driver=self.__driver)
        self.__driver.create_node(name=self.name, image=image,
                                  size=size, blockdevicemappings=ebs.get_block_device_mapping())
        print("EC2 successfully deployed")

    def get_images(self):
        images = []
        for imageID in self.__free_tier_images:
            images.append(self.__driver.get_image(imageID))
        return images

    def get_sizes(self):
        sizes = self.__driver.list_sizes()
        return sizes

        
    




