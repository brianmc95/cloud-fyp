"""
    Brian McCarthy 114302146
    114302146@umail.ucc.ie
    brianmccarthy95@gmail.com

    Class to represent an Amazon EC2 instance.
"""

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage
import json


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
                 userdata=None, security_groups=[], security_group_ids=[], metadata=None,
                 mincount=1, maxcount=1, clienttoken="", associated_ebs_volumes=[],
                 ebs_optimized=True, subnet=None, placement_group=None, assign_public_id=True,
                 terminate_on_shutdown=True, accessID_Local=".", accessKey_Local="."):
        # Initial setup of EC2 instance.
        self.user = user
        self.name = name
        self.imageID = imageID
        self.size = size
        self.region = region
        self.keyname = keyname
        self.userdata = userdata
        self.security_groups = security_groups
        self.security_grous_ids = security_group_ids
        self.metadata = metadata
        self.mincount = mincount
        self.maxcount = maxcount
        self.clienttoken = clienttoken
        self.associated_ebs_volumes = associated_ebs_volumes
        self.ebs_optimized = ebs_optimized
        self.subnet = subnet
        self.placement_group = placement_group
        self.assign_public_ip = assign_public_id
        self.terminate_on_shutdown = terminate_on_shutdown

        self.__accessID, self.__accessKey = self.__read_in_access_keys(accessID_Local, accessKey_Local)

        self.__cls = get_driver(Provider.EC2)
        self.__driver = self.__cls(self.__accessID, self.__accessKey, region=self.region)

    def __str_(self):
        return "%s: %s, %s, %s, %s" % (self.name, self.imageID, self.region,
                                       self.associated_ebs_volumes, self.keyname)

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

    def set_userdata(self, userdata):
        # Any user data associated with this EC2 instance
        self.userdata = userdata

    def set_security_groups(self, security_groups):
        # Security group(s) this instance is associated with
        self.security_groups = security_groups

    def set_security_group_ids(self, security_group_ids):
        # Special form of security group
        self.security_grous_ids = security_group_ids

    def set_metadata(self, metadata):
        # key/value metadata associated with this instance
        self.metadata = metadata

    def set_mincount(self, mincount):
        # Minimum number of this EC2 image to instantiate
        self.mincount = mincount

    def set_maxcount(self, maxcount):
        # Maximum number of this EC2 image to instantiate
        self.maxcount = maxcount

    def set_clienttoken(self, clienttoken):
        # Unique identifier for this EC2 instance
        self.clienttoken = clienttoken

    def set_associated_ebs_volumes(self, volumes):
        # EBS volumes associated with this EC2 instance.
        self.EBS_volumes = volumes

    def set_ebs_optimized(self, ebs_optimized):
        # Boolean representing if this EC2 is optimized for EBS
        self.ebs_optimized = ebs_optimized

    def set_subnet(self, subnet):
        # Subnet this EC2 is located in
        self.subnet = subnet

    def set_placement_group(self, placement_group):
        # Name of placement group this EC2 is in
        self.placement_group = placement_group

    def set_assign_public_ip(self, assign_public_ip):
        # Boolean to represent if EC2 should have a public ip address
        self.assign_public_ip = assign_public_ip

    def set_terminate_on_shutdown(self, terminate_on_shutdown):
        # Boolean representing if when shutdown this EC2 should terminate
        self.terminate_on_shutdown = terminate_on_shutdown

    def set_ip_addr(self, ip_addr):
        # Setter to get the IP address of the EC2 instance
        self.ip_addr = ip_addr

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

    def get_userdata(self):
        # return any user data associated with this EC2 instance
        return self.userdata

    def get_security_groups(self):
        # return Security group(s) this instance is associated with
        return self.security_groups

    def get_security_group_ids(self):
        # return Special form of security group (for vpc instances)
        return self.security_grous_ids

    def get_metadata(self):
        # return key/value metadata associated with this instance
        return self.metadata

    def get_mincount(self):
        # return Minimum number of this EC2 image to instantiate
        return self.mincount

    def get_maxcount(self):
        # return Maximum number of this EC2 image to instantiate
        return self.maxcount

    def get_clienttoken(self):
        # return Unique identifier for this EC2 instance
        return self.clienttoken

    def get_associated_ebs_volumes(self):
        # return EBS volumes associated with this EC2 instance.
        return self.EBS_volumes

    def get_ebs_optimized(self):
        # return Boolean representing if this EC2 is optimized for EBS
        return self.ebs_optimized

    def get_subnet(self):
        # return Subnet this EC2 is located in
        return self.subnet

    def get_placement_group(self):
        # return Name of placement group this EC2 is in
        return self.placement_group

    def get_assign_public_ip(self):
        # return Boolean to represent if EC2 should have a public ip address
        return self.assign_public_ip

    def get_terminate_on_shutdown(self):
        # return Boolean representing if when shutdown this EC2 should terminate
        return self.terminate_on_shutdown

    def instantiate_ec2(self):
        # Instantiate the EC2 instance.
        sizes = self.__driver.list_sizes(self.region)
        size = [s for s in sizes if s.id == self.size][0]
        image = NodeImage(id=self.imageID, name=self.name, driver=self.__driver)
        self.__driver.create_node(name=self.name, image=image, size=size)
        print("EC2 successfully deployed")

def main():
    myEC2 = EC2("me", "myEC2", "ami-acd005d5", "t2.micro",
                "eu-west-1", "firstTestInstance",
                accessID_Local="/Users/BrianMcCarthy/amazonKeys/accessID",
                accessKey_Local="/Users/BrianMcCarthy/amazonKeys/sak2")
    myEC2.instantiate_ec2()

if __name__ == "__main__":
    main()

        
    




