import click

class Config():

    def __init__(self):
        self.verbose = False


pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option("--verbose", "-v", is_flag=True)
@pass_config
def cli(config, verbose):
    """
    CLI Service to go alongside the cloud management system. Each sub-service described below:
    """
    config.verbose = verbose
    if verbose:
        click.echo("Logging in verbose mode")

@cli.command()
@click.option("--provider", "-pv", help="Provider with which to deploy a node to.")
@click.option("--image", "-i", help="ImageID of image you wish to deploy the node with")
@click.option("--size", "-s", help="SizeID of size you wish to deploy the node with")
@click.option("--networks", "-n", help="ID of networks required for deployed node", multiple=True)
@click.option("--security_groups", "-sg", help="ID of security groups to add to the deployed node", multiple=True)
@pass_config
def deploy(config, provider, image, size, networks, secuirty_groups):
    """
    Allows for the deployment of instances to a specified provider with options described in deploy --help
    """
    click.echo("Deploy node")

@cli.command()
@click.option("--provider", "-pv", help="Provider with which you want a description of it's options")
@click.option("--images", "-i", is_flag=True)
@click.option("--sizes", "-s", is_flag=True)
@click.option("--networks", "-n", is_flag=True)
@click.option("--security-groups", "-sg", is_flag=True)
@pass_config
def deploy_options(config, images, sizes, networks, security_groups):
    """
    Provides a description of all the options a provider has when deploying an instance.
    """
    click.echo("Describe options")

@cli.command()
@pass_config
def monitor(config):
    """
    Service to monitor instances across multiple providers
    """
    click.echo("Monitor Node")

@cli.command()
@pass_config
def migration(config):
    """
    Service to migrate an instance from one provider to another
    """
    click.echo("Migration service")

@cli.command()
@pass_config
def key_management(config):
    click.echo("Key Management service")

@cli.group()
@pass_config
def account(config):
    """
    Allows for the configuration of cloud provider accounts.
    """
    click.echo("Account management")

@account.command()
@pass_config
def aws_account(config):
    """
    Functionality to configure an AWS account
    """
    click.echo("Create aws account")

@account.command()
@pass_config
def openstack_account(config):
    """
    Functionality to configure an OpenStack account
    """
    click.echo("Create openstack account")
