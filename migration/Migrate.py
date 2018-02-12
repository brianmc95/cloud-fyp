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

        self.aws_prov = AWSProvider()
        self.os_prov = OpenStackProvider()

    def deploy_S3(self):
        attempts = 0
        while True:
            try:
                attempts += 1
                randomName = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                container = self.aws_prov.create_container(randomName)
                return container
            except InvalidContainerNameError:
                if attempts > 3:
                    raise InvalidContainerNameError
                continue

    def connect_to_node(self):
        ip = self.node.public_ips[0]
        self.ssh = paramiko.SSHClient()

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh.connect(ip, username='ubuntu', password='',
                    key_filename=self.node_key_file_loc)

    def copy_image(self):
        # TODO: 1) Find the volume size and type ... type may be less important Done
        # TODO: 2) Create a volume of the same size on AWS
        # TODO: 3) Attach that volume to the instance
        # TODO: 4) Partition, format and mount the disk
        # TODO: 5) Copy the disk to an image file
        block_devices = self.node.extra["block_device_mapping"]
        self.__location = self.node.extra["availability"]

        for vol in block_devices:
            volume_id = vol["ebs"]["volume_id"]
            self.__vols.append(self.aws_prov.get_volume(volume_id))
        migration_vols = []
        vol_count = 0

        mounts = "abcdefghijklmnopqrstuvwxyz"
        for vol in self.__vols:
            migrate_vol = self.aws_prov.create_volume("migration_vol", vol.size, location=self.__location)
            migration_vols.append(migrate_vol)

            device_name = "/dev/xvd{}".format(mounts[vol_count])
            mount_point = "tmp/disk{}".format(vol_count)

            success = self.aws_prov.attach_volume(self.node, migrate_vol, device=device_name)

            stdin, stdout, stderr = self.ssh.exec_command("lsblk")
            for line in stdout.readlines():
                print(line.split())
            for line in stderr.readlines():
                print(line, end="")

            stdin, stdout, stderr = self.ssh.exec_command("sudo mkfs -t ext4 {}".format(device_name))
            for line in stdout.readlines():
                print(line, end="")
            for line in stderr.readlines():
                print(line, end="")

            stdin, stdout, stderr = self.ssh.exec_command("sudo mkdir {}".format(mount_point))
            for line in stdout.readlines():
                print(line, end="")
            for line in stderr.readlines():
                print(line, end="")

            stdin, stdout, stderr = self.ssh.exec_command("sudo mount {} {}".format(device_name, mount_point))
            for line in stdout.readlines():
                print(line, end="")
            for line in stderr.readlines():
                print(line, end="")

            stdin, stdout, stderr = self.ssh.exec_command("sudo dd if={} of={}/disk.img".format(device_name, mount_point))
            for line in stdout.readlines():
                print(line, end="")
            for line in stderr.readlines():
                print(line, end="")

            vol_count += 1

    def transfer_image(self, container):
        # TODO: 0) Possibly create the s3 bucket
        # TODO: 1) Add AWS credentials to the remote instance (the being copied) or else upload the thing using libcloud
        # TODO: 2) Copy the image file to the s3 bucket
        # TODO: 3) Unmount and delete the volume
        # TODO: 4) Copy image from s3 to local
        # Create the container if it doesn't exist
        if container is None:
            container = self.deploy_S3()
        bucket_name = container.name

        # Add aws credentials to the instance to be copied.
        aws_access_id, aws_secret_key = self.aws_prov.get_key_info()
        stdin, stdout, stderr = self.ssh.exec_command("""aws configure set aws_access_key_id {};
        aws configure set aws_secret_access_key {};
        aws configure set default.region {}""").format(aws_access_id, aws_secret_key, self.__location)
        for line in stdout.readlines():
            print(line, end="")
        for line in stderr.readlines():
            print(line, end="")

        # Copy each volume to the s3
        vol_count = 0
        for vol in self.__vols:
            self.ssh.exec_command("aws s3 cp/tmp/disk{} s3://{}/".format(i, bucket_name))
            for line in stdout.readlines():
                print(line, end="")
            for line in stderr.readlines():
                print(line, end="")

            # Once copied to the s3 dettach and destroy the volume
            self.aws_prov.dettach_volume(self.node, vol)
            self.aws_prov.destroy_volume(vol)


    def create_new_node(self):
        # TODO: 0) Optionally destroy the instance itself
        # TODO: 1) Create image from the raw disk image
        # TODO: 2) Create node from this image
        # extra: Check if we need a means of translating the sizes and such
        raise NotImplementedError
