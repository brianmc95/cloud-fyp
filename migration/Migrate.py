"""
    Script to migrate a VM from aws to openstack
    and the reverse ... I hope
"""

from accounts.AWSProvider import AWSProvider
from accounts.OpenStackProvider import OpenStackProvider
from libcloud.storage.types import InvalidContainerNameError
import random
import string
import paramiko
from glanceclient import Client
import logging
import time


class Migrate:

    def __init__(self, node, fromaws, node_key_file_loc, container=None, user=None, password=None):
        self.node = node
        self.fromaws = fromaws
        self.node_key_file_loc = node_key_file_loc
        self.container = container
        self.ssh = None
        self.user = user
        self.password = password
        self.__location = None
        self.__vols = []
        self.__migration_vols = []

        self.logger = logging.getLogger(__name__)

        self.aws_prov = AWSProvider()
        self.os_prov = OpenStackProvider()

    def deploy_S3(self):
        """
        Method to create a randomly identifiable S3 bucket.
        :return: None
        """
        attempts = 0
        while True:
            try:
                self.logger.debug("Attempt number {} to create S3".format(attempts))
                attempts += 1
                randomName = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                randomName = randomName.lower()
                self.logger.debug("Random name for S3 {}".format(randomName))
                container = self.aws_prov.create_container(randomName)
                self.logger.info("S3 Bucket {} created".format(randomName))
                return container
            except InvalidContainerNameError as e:
                if attempts > 3:
                    self.logger.exception("Failed to create an S3")
                    raise InvalidContainerNameError
                continue

    def connect_to_node(self):
        """
        Function to connect to the node which is to be migrated
        :return: None
        """
        ip = self.node.public_ips[0]
        self.logger.debug("IP Address of node to be migrated: {}".format(ip))
        self.ssh = paramiko.SSHClient()

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh.connect(ip, username='ubuntu', password='',
                         key_filename=self.node_key_file_loc)

        self.logger.info("Connection created to node to be migrated.")

    def copy_image_local(self):
        """
        Function to copy the root volume of a node to a newly created node of the same size
        :return: None
        """

        block_devices = self.node.extra["block_device_mapping"]
        self.__location = self.node.extra["availability"]
        self.logger.debug("Location of aws node to be migrated {}".format(self.__location))

        for vol in block_devices:
            volume_id = vol["ebs"]["volume_id"]
            self.__vols.append(self.aws_prov.get_volume(volume_id))
            self.logger.debug("Volume attached to the migrated instance {}".format(volume_id))

        migration_vols = []
        vol_count = 0
        mounts = "fghijklmnop"
        for vol in self.__vols:
            # Migration volumes need to be slightly larger than the ones being copied to them
            migrate_vol = self.aws_prov.create_volume("migration_vol", vol.size + 2, location=self.__location)
            self.__migration_vols.append(migrate_vol)

            device_name = "/dev/xvd{}".format(mounts[vol_count])
            mount_point = "/tmp/disk{}".format(vol_count)
            self.logger.info("Device attached: {}, Mount Point: {}, Size: {}".format(device_name,
                                                                                     mount_point,
                                                                                     vol.size))

            success = self.aws_prov.attach_volume(self.node, migrate_vol, device=device_name)
            time.sleep(120)

            if not success:
                self.logger.critical("Volume could not be attached")
                return
            self.logger.info("Volume attached")

            cmd = "sudo mkfs.ext4 {}".format(device_name)
            self.logger.debug("Command to be run: {}".format(cmd))
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            self.logger.info(stdout.readlines())
            self.logger.warning(stderr.readlines())

            cmd="sudo mkdir {}".format(mount_point)
            self.logger.debug("Command to be run: {}".format(cmd))
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            self.logger.info(stdout.readlines())
            self.logger.warning(stderr.readlines())

            cmd = "sudo mount {} {}".format(device_name, mount_point)
            self.logger.debug("Command to be run: {}".format(cmd))
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            self.logger.info(stdout.readlines())
            self.logger.warning(stderr.readlines())

            cmd = "sudo dd if=/dev/xvda of={}/disk{}.img".format(mount_point, vol_count)
            self.logger.debug("Command to be run: {}".format(cmd))
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            self.logger.info(stdout.readlines())
            self.logger.warning(stderr.readlines())

            vol_count += 1
            self.logger.info("Volume image successfully copied.")

    def transfer_image_to_s3(self, container):
        """
        Method to transfer the image from the new volume to the provided S3
        :param container: S3 Bucket we are to transfer the img file to.
        :return: None
        """
        bucket_name = container.name

        # Add aws credentials to the instance to be copied.
        aws_access_id, aws_secret_key = self.aws_prov.get_key_info()
        # TODO: Add step to check if awscli is installed if not then install it manually
        stdin, stdout, stderr = self.ssh.exec_command("""aws configure set aws_access_key_id {};
        aws configure set aws_secret_access_key {};
        aws configure set default.region {}""".format(aws_access_id, aws_secret_key, self.__location))
        self.logger.info(stdout.readlines())
        self.logger.warning(stderr.readlines())

        # Copy each volume to the s3
        vol_count = 0
        for vol in self.__migration_vols:
            self.ssh.exec_command("aws s3 cp /tmp/disk{}.img s3://{}/".format(vol_count, bucket_name))
            self.logger.info(stdout.readlines())
            self.logger.warning(stderr.readlines())

            # Once copied to the s3 detach and destroy the volume
            self.aws_prov.detach_volume(vol)
            time.sleep(300) # sometimes run into issues with this.
            self.aws_prov.destroy_volume(vol)
            self.logger.info("Volume removed and destroyed")

            vol_count += 1
        return vol_count

    def pull_image(self, container, file_name, dest):
        """
        Dowload the image file to be turned into a node
        :param container: container to pull the disk from.
        :param file_name: file to be pulled i.e. the image file.
        :param dest: Location where image file should be placed.
        :return: None
        """
        # Download the image file
        success = self.aws_prov.download_from_container(container, file_name, dest)
        if not success:
            self.logger.error("Failed to download the img file from s3")
            return

    def create_image(self, image_file_loc):
        raise NotImplementedError



    def create_node(self):
        print("Glance part")
