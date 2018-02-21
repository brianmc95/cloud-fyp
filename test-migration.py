#!/usr/bin/env python3

from migration.Migrate import Migrate
from accounts.AWSProvider import AWSProvider
import os


def run_test():

    try:

        aws_provider = AWSProvider()
        migration_node = aws_provider.get_node("test-migration")
        node_key_loc = "/Users/BrianMcCarthy/amazonKeys/firstTestInstance.pem"

        mig = Migrate(migration_node, True, node_key_loc)
    #   s3 = mig.deploy_S3()
        mig.connect_to_node()
    #   mig.copy_image_local()
    #   volumes = mig.transfer_image_to_s3(s3)
    #
    #   try:
    #       os.mkdir("~/test-migration")
    #   except FileExistsError:
    #       print("test-migration folder is already created.")
    #
    #   for i in range(volumes):
    #       mig.pull_image(s3, "disk{}.img".format(i), "~/test-migration/")
    #       mig.create_node()
    #
    except Exception as e:
         print(e)
    #     # Destroy the node and associated volumes
    #     aws_provider.destroy_node(migration_node)
    #
    #     # Recreate Node
    #     mig_image = aws_provider.get_image("ami-4b671032")
    #     mig_size = aws_provider.get_size("t2.micro")
    #     mig_sec = aws_provider.get_security_groups("launch-wizard-1")
    #     mig_net = aws_provider.get_networks("subnet-82cb7ed9")
    #     mig_key = aws_provider.list_key_pairs()[0]
    #     migration_node = aws_provider.create_node("test-migration", mig_size, mig_image, mig_net, mig_sec, mig_key.name)


if __name__ == "__main__":
    run_test()
