import click
import datetime
import requests
import json

class Config:

    def __init__(self):
        self.verbose = False
        self.manager_ip = "127.0.0.1"
        self.manager_port = 8080


pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option("--verbose", "-v", is_flag=True)
@click.option("--ip", "-i", nargs=1, default="127.0.0.1", help="The IP address of the manager node")
@click.option("--port", "-p",nargs=1, default=8080, help="The port on which the manager node is listening")
@pass_config
def cli(config, verbose, ip, port):
    """
    CLI Service to go alongside the cloud management system. Each sub-service described below:
    """
    config.verbose = verbose
    config.manager_ip = ip
    config.manager_port = port

@cli.command()
@click.option("--provider", "-pr", type=click.Choice(["aws", "openstack"]), help="Provider you wish to interact with")
@click.option("--name", "-n", help="Name of the instance you wish to build")
@click.option("--image", "-i", help="ImageID of image you wish to deploy the node with")
@click.option("--size", "-s", help="SizeID of size you wish to deploy the node with")
@click.option("--networks", "-nt", multiple=True, help="ID of networks required for deployed node")
@click.option("--securityGroups", "-sg", multiple=True, help="ID of security groups to add to the deployed node")
@click.option("--keyName", "-k", help="Name of keypair with which you will access the node")
@pass_config
def deploy(config, name, provider, image, size, networks, securitygroups, keyname):
    """
    Allows for the deployment of instances to a specified provider with specified options.
    For AWS networks, use the network name, in all other cases use the id associated with that variable
    """
    try:
        payload = {"NAME": name,
                   "PROVIDER": provider,
                   "IMAGE": image,
                   "SIZE": size,
                   "NETWORKS": networks,
                   "SECURITY_GROUPS": securitygroups,
                   "KEY_NAME": keyname}
        set_url = "http://{}:{}/deploy/".format(config.manager_ip, config.manager_port)
        r = requests.post(set_url, data=json.dumps(payload))

        if r.status_code == 200:
            response = r.content
            click.echo(response)
            click.echo("Node: {} successfully deployed".format(name))
            return 0
        else:
            click.echo("Node: {} was not able to be deployed".format(name))
            return 1
    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))

@cli.command()
@click.option("--provider", "-pr", type=click.Choice(["aws", "openstack"]), help="Provider you wish to interact with")
@click.option("--name", "-n", help="Name of the instance you wish to destroy")
@click.option("--nodeID", "-id", help="ID of the instance to be destoryed")
@pass_config
def delete_node(config, provider, name, nodeid):
    """
    Allows for the deletion of a node of a particular provider.
    """
    try:
        payload = {"NODE_NAME": name,
                   "PROVIDER": provider,
                   "NODE_ID": nodeid}
        set_url = "http://{}:{}/delete-node/".format(config.manager_ip, config.manager_port)
        r = requests.post(set_url, json=json.dumps(payload))

        if r.status_code == 200:
            response = r.content
            click.echo(response)
            click.echo("Node: {} successfully delted".format(name))
            return 0
        else:
            click.echo("Node: {} was not able to be deleted".format(name))
            return 1
    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))

@cli.command()
@click.option("--provider", "-pr", type=click.Choice(["aws", "openstack"]), help="Provider you wish to interact with")
@click.option("--images", "-i", is_flag=True, help="List image options")
@click.option("--sizes", "-s", is_flag=True, help="List size options")
@click.option("--networks", "-n", is_flag=True, help="List network options")
@click.option("--securityGroups", "-sg", is_flag=True, help="List security group options")
@pass_config
def deploy_options(config, provider, images, sizes, networks, securitygroups):
    """
    Provides a description of all the options a provider has when deploying an instance.
    """
    try:
        payload = {"PROVIDER": provider,
                   "IMAGES": images,
                   "SIZES": sizes,
                   "NETWORKS": networks,
                   "SECURITY_GROUPS": securitygroups}
        set_url = "http://{}:{}/deploy-options/".format(config.manager_ip, config.manager_port)
        r = requests.post(set_url, data=json.dumps(payload))

        if r.status_code == 200:
            click.echo(r.json())
            return 0
        else:
            click.echo("Was unable to obtain information")
        return 1
    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))

@cli.command()
@click.option("--year", "-y", help="Year you wish to get data for")
@click.option("--month", "-m", help="Month you wish to get data for. Requires year")
@click.option("--day", "-d", help="Day you wish to get data for. Requires month")
@click.option("--current", "-c", is_flag=True, help="Get data for the current moment")
@click.option("--instanceID", "-id", default=None, help="ID of the instance you want data for.")
@pass_config
def monitor(config, year, month, day, current, instanceid):
    """
    Service to monitor instances across multiple providers
    """
    try:
        payload = {
            "YEAR": year,
            "MONTH": month,
            "DAY": day,
            "INSTANCE_ID": instanceid,
            "CURRENT": current
        }
        set_url = "http://{}:{}/monitor/".format(config.manager_ip, config.manager_port)
        r = requests.post(set_url, data=json.dumps(payload))
        if r.status_code == 200:
            response = r.json()
            click.echo(response)
            return 0
        click.echo("Unable to obtain monitoring information")
        return 1
    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))

@cli.command()
@click.option("--source", "-s", type=click.Choice(["aws", "openstack"]), help="Provider from which you want to migrate")
@click.option("--instanceID", "-id", help="ID of the instance you want data for.")
@pass_config
def migration(config, source, instanceid):
    """
    Service to migrate an instance from one provider to another
    """
    #TODO: Implement with migration branch
    click.echo("Migration service")

@cli.command()
@click.option("--provider", "-pr", type=click.Choice(["aws", "openstack"]), help="Provider you wish to interact with")
@click.option("--keyName", "-kn", default="", help="Name of key [Unnecessary for upload/list]")
@click.option("--keyLocation", "-kl", type=click.Path(), help="Location of key to upload/location to download the key to.")
@click.option("--upload", "-u", is_flag=True, help="Whether to upload a key file")
@click.option("--download", "-d", is_flag=True, help="Whether to download a key file")
@click.option("--listKeys", "-lk", is_flag=True, help="Whether to list all key files")
@click.option("--deleteKey", "-dl", is_flag=True, help="Key File to be deleted")
@pass_config
def key_management(config, provider, keyname, keylocation, download, upload, listkeys, deletekey):
    """
    Service to manage keys.\n
    download: Download key [Boolean] \n
    upload: Upload key [Boolean] \n
    list: list available keys [Boolean] \n
    """
    payload = {
        "PROVIDER": provider,
        "OPERATION": None,
        "KEY_NAME": keyname,
        "KEY_VALUE": ""
    }
    try:
        if upload:
            payload["OPERATION"] = "UPLOAD"
            upload_url = "http://{}:{}/key/".format(config.manager_ip, config.manager_port)
            with open(keylocation) as keyfile:
                payload["KEY_NAME"] = keyfile.name
                payload["KEY_VALUE"] = keyfile.read()
            r = requests.post(upload_url, data=json.dumps(payload))
            if r.status_code == 200:
                click.echo("Key {} successfully uploaded".format(payload["KEY_NAME"]))
                return 0
            click.echo("Key {} was unable to be uploaded".format(payload["KEY_NAME"]))
            return 1

        if download:
            payload["OPERATION"] = "DOWNLOAD"
            upload_url = "http://{}:{}/key/".format(config.manager_ip, config.manager_port)
            r = requests.post(upload_url, data=json.dumps(payload))
            if r.status_code == 200:
                response = r.json()
                if keylocation is None:
                    key_location = response["KEY_NAME"]
                else:
                    key_location = "{}{}".format(keylocation, response["KEY_NAME"])
                with open(key_location, "w") as key_file:
                    key_file.write(response["KEY_VALUE"])
                click.echo("Key {} successfully downloaded".format(payload["KEY_NAME"]))
                return 0
            click.echo("Key {} was unable to be downloaded".format(payload["KEY_NAME"]))
            return 1

        if listkeys:
            payload["OPERATION"] = "LIST"
            upload_url = "http://{}:{}/key/".format(config.manager_ip, config.manager_port)
            r = requests.post(upload_url, data=json.dumps(payload))
            if r.status_code == 200:
                click.echo(r.json())
                return 0
            click.echo("Unable to list available keys")
            return 1

        if deletekey:
            payload["OPERATION"] = "DELETE"
            upload_url = "http://{}:{}/key/".format(config.manager_ip, config.manager_port)
            r = requests.post(upload_url, data=json.dumps(payload))
            if r.status_code == 200:
                click.echo("Key {} successfully deleted".format(payload["KEY_NAME"]))
                return 0
            click.echo("Key {} was unable to be deleted".format(payload["KEY_NAME"]))
            return 1

    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))
    except IOError as e:
        click.echo(e)
        click.echo("Was unable to find file at location {}".format(keylocation))

@cli.command()
@click.option("--provider", "-pr", type=click.Choice(["aws", "openstack"]), help="Provider you wish to interact with")
@click.option("--accountName", "-an", default="", help="Name of the account you wish to set (only used with setAccount)")
@click.option("--setAccount", "-s", is_flag=True, help="Set account that nodes will be created with")
@click.option("--listAccounts", "-l", is_flag=True, help="List accounts available to use")
@click.option("--deleteAccount", "-d", is_flag=True, help="Delete the named account")
@pass_config
def account(config, provider, accountname, setaccount, listaccounts, deleteaccount):
    """
    Allows for the management of accounts.\n
    """
    try:
        payload = {
            "PROVIDER": provider,
            "ACCOUNT_NAME": accountname
        }
        if setaccount:
            set_url = "http://{}:{}/account/set/".format(config.manager_ip, config.manager_port)
            r = requests.post(set_url, data=json.dumps(payload))
            if r.status_code == 200:
                click.echo("Account: {} successfully set account for provider {}".format(accountname, provider))
                return 0
            click.echo("Failed to set account {} for provider {}".format(accountname, provider))
            return 1

        if listaccounts:
            set_url = "http://{}:{}/account/list/".format(config.manager_ip, config.manager_port)
            r = requests.post(set_url, data=json.dumps(payload))
            if r.status_code == 200:
                click.echo(r.json())
                return 0
            click.echo("Failed to list accounts for provider {}".format(provider))
            return 1

        if deleteaccount:
            set_url = "http://{}:{}/account/delete/".format(config.manager_ip, config.manager_port)
            r = requests.post(set_url, data=json.dumps(payload))
            if r.status_code == 200:
                click.echo("Successfully delete account {} for provider {}".format(accountname, provider))
                return 0
            click.echo("Failed to delete account {} for provider {}".format(accountname, provider))
            return 1

    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))
    except IOError as e:
        click.echo(e)
        click.echo("Was unable to find file at location")


@cli.command()
@click.option("--accountName", "-an", help="Name of the account you are creating.")
@click.option("--accountID", "-ai", help="ID associated with the account.")
@click.option("--region", "-r", help="Region in which the account will operate.")
@click.option("--secretKey", "-s", help="Location of secret key on system.")
@pass_config
def aws_account(config, accountname, accountid, region, secretkey):
    """
    Functionality to configure an AWS account
    """
    payload = {
        "ACCOUNT_NAME": accountname,
        "ACCOUNT_ID": accountid,
        "ACCOUNT_REGION": region,
        "ACCOUNT_SECRET_KEY": None,
        "PROVIDER": "aws",
        "SET_ACCOUNT": False
    }
    try:
        with open(secretkey, "r") as secret_key_file:
            payload["ACCOUNT_SECRET_KEY"] = secret_key_file.read().strip()
        set_url = "http://{}:{}/account/add/".format(config.manager_ip, config.manager_port)
        r = requests.post(set_url, data=json.dumps(payload))
        if r.status_code == 200:
            click.echo("Account {} successfully added".format(accountname))
            return 0
        click.echo("Failed to add account {}".format(accountname))
        return 1
    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))
    except IOError as e:
        click.echo(e)
        click.echo("Was unable to find file at location")

@cli.command()
@click.option("--accountName", "-an", help="Name of the account you are creating")
@click.option("--accountID", "-ai", help="ID of the account you are creating")
@click.option("--authorizationURL", "-au", help="URL of the OpenStack instsnce you are accessing")
@click.option("--authorizationVersion", "-av", help="Authorization version of the OpenStack instance you are accessing")
@click.option("--tenantName", "-t", help="Tenant name associated with the account")
@click.option("--glanceVersion", "-g", help="Version of glance image api for OpenStack used")
@click.option("--password", "-pw", help="Password associated with the account")
@click.option("--projectID", "-pi", help="ID of the project the account is associated with")
@pass_config
def openstack_account(config, accountname, accountid, authorizationurl, authorizationversion, tenantname, glanceversion, password, projectid):
    """
    Functionality to configure an OpenStack account
    """
    payload = {
        "ACCOUNT_NAME": accountname,
        "ACCOUNT_ID": accountid,
        "ACCOUNT_AUTH_URL": authorizationurl,
        "ACCOUNT_AUTH_VERSION": authorizationversion,
        "ACCOUNT_IMAGE_VERSION": glanceversion,
        "ACCOUNT_TENANT_NAME": tenantname,
        "ACCOUNT_PASSWORD": password,
        "ACCOUNT_PROJECT_ID": projectid,
        "PROVIDER": "openstack",
        "SET_ACCOUNT": False
    }
    try:
        set_url = "http://{}:{}/account/add/".format(config.manager_ip, config.manager_port)
        r = requests.post(set_url, data=json.dumps(payload))
        if r.status_code == 200:
            click.echo("Account {} successfully added".format(accountname))
            return 0
        click.echo("Failed to add account {}".format(accountname))
        return 1
    except requests.exceptions.HTTPError as errh:
        click.echo("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        click.echo("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        click.echo("Timeout Error: {}".format(errt))
    except requests.exceptions.RequestException as err:
        click.echo("ERROR: {}".format(err))
