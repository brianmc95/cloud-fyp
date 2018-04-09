from pymongo import MongoClient
import pymongo.errors
import json
import pandas as pd
import datetime
import os
from accounts.OpenStack import OpenStack
from accounts.AWS import AWS
import logging


class DataManager:

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client["cloud-fyp"]
        self.inst_info = self.db["instances"]
        self.inst_use = self.db["instance_usages"]
        self.vols = self.db["volumes"]
        self.accounts = self.db["accounts"]
        self.__root_path = self.__get_root_path()
        self.__keys_dir = "keys"
        self.aws_prov, self.open_prov = self.setup_drivers()

    def setup_drivers(self):
        aws_account = self.get_set_account("aws")
        open_account = self.get_set_account("openstack")
        self.logger.info("Set aws account is {}".format(aws_account))
        self.logger.info("Set openstack account is {}".format(open_account))
        aws_prov = None
        open_prov = None
        if aws_account:
            aws_prov = AWS(aws_account["ACCOUNT_ID"], aws_account["ACCOUNT_SECRET_KEY"],
                                aws_account["ACCOUNT_REGION"])
        if open_account:
            open_prov = OpenStack(open_account["ACCOUNT_ID"], open_account["ACCOUNT_PASSWORD"],
                                  open_account["ACCOUNT_AUTH_URL"], open_account["ACCOUNT_AUTH_VERSION"],
                                  open_account["ACCOUNT_TENANT_NAME"], open_account["ACCOUNT_PROJECT_ID"],
                                  open_account["ACCOUNT_IMAGE_VERSION"])
        return aws_prov, open_prov

    def get_drivers(self):
        return self.aws_prov, self.open_prov

    def __get_root_path(self):
        full_path = os.getcwd()
        root_path = ""
        for directory in full_path.split('/'):
            if directory == "cloud-fyp":
                root_path += directory
                return root_path
            root_path += "{}/".format(directory)

    def add_account(self, account):
        try:
            insert_id = self.accounts.insert_one(account).inserted_id
            if insert_id:
                self.logger.info("Successfully added the account, inserted in {}".format(insert_id))
                return True
            self.logger.info("Was unable to inser the account")
            return False
        except pymongo.errors.ConnectionFailure as e:
            self.logger.exception("Could not access the MongoDB")
            self.logger.exception(e)
            return False
        except Exception as e:
            self.logger.exception("Something went very wrong")
            self.logger.exception(e)
            return False

    def get_accounts(self, provider=None):
        try:
            if provider:
                accounts = []
                for document in self.accounts.find({"PROVIDER": provider}, {'_id': False}):
                    account = {"ACCOUNT_NAME": document["ACCOUNT_NAME"],
                            "PROVIDER": document["PROVIDER"],
                            "SET_ACCOUNT": document["SET_ACCOUNT"]}
                    accounts.append(account)
                self.logger.debug("Retrieved accounts for provider {}, accounts are {}".format(provider, accounts))
                return accounts
            else:
                return list(self.accounts.find({}, {'_id': False}))
        except pymongo.errors.ConnectionFailure as e:
            self.logger.exception("Could not access the MongoDB")
            self.logger.exception(e)
            return False

    def set_account(self, account_name, provider):
        try:
            result_unset = self.accounts.update_one({"PROVIDER": provider, "SET_ACCOUNT": True}, {"$set": {"SET_ACCOUNT": False}})
            result_set = self.accounts.update_one({"ACCOUNT_NAME": account_name, "PROVIDER": provider}, {"$set": {"SET_ACCOUNT": True}})
            if result_set.modified_count > 0 and (result_unset.matched_count > 0 and result_unset.modified_count > 0) or result_unset.matched_count == 0:
                self.aws_prov, self.open_prov = self.setup_drivers()
                self.logger.info("Successfully set account {} for provider {}".format(account_name, provider))
                return True
            return False
        except pymongo.errors.ConnectionFailure as e:
            self.logger.exception("Could not access the MongoDB")
            self.logger.exception(e)
            return False

    def get_set_account(self, provider):
        try:
            set_account = self.accounts.find_one({"PROVIDER": provider, "SET_ACCOUNT": True}, {'_id': False})
            self.logger.info("Set account retrieved {}".format(set_account))
            return set_account
        except pymongo.errors.ConnectionFailure as e:
            self.logger.exception("Could not access the MongoDB")
            self.logger.exception(e)
            return False

    def delete_account(self, account_name, provider):
        try:
            delete_account = self.accounts.delete_one({"PROVIDER": provider, "ACCOUNT_NAME": account_name})
            if delete_account.deleted_count > 0:
                self.logger.info("Account {} for provider {} deleted successfully".format(account_name, provider))
                return True
            return False
        except pymongo.errors.ConnectionFailure as e:
            self.logger.exception("Could not access the MongoDB")
            self.logger.exception(e)
            return False

    def add_key(self, data):
        try:
            key_dir = "{}/{}".format(self.__root_path, self.__keys_dir)
            if not os.path.isdir(key_dir):
                os.mkdir(key_dir)
            key_dir = "{}/{}".format(key_dir, data["PROVIDER"])
            if not os.path.isdir(key_dir):
                os.mkdir(key_dir)
            with open("{}/{}".format(key_dir, data["KEY_NAME"]), "w") as key_file:
                key_file.write(data["KEY_VALUE"])
                os.chmod("{}/{}".format(key_dir, data["KEY_NAME"]), 0o600)
                self.logger.info("Key {} added for provider {}".format(data["KEY_NAME"], data["PROVIDER"]))
        except Exception as e:
            self.logger.exception("Could not add the key")
            self.logger.exception(e)
            return False
        return True

    def get_keys(self, provider):
        if provider == "aws" or provider == "openstack":
            return os.listdir("{}/{}/{}/".format(self.__root_path, self.__keys_dir, provider))
        return []

    def get_key(self, provider, key_name):
        if provider == "aws" or provider == "openstack":
            return "{}/{}/{}/{}.pem".format(self.__root_path, self.__keys_dir, provider, key_name)

    def download_key(self, provider, key_name):
        try:
            result = {
                "KEY_NAME": key_name,
                "KEY_VALUE": ""
            }
            with open("{}/{}/{}/{}".format(self.__root_path, self.__keys_dir, provider, key_name), "r") as keyfile:
                result["KEY_VALUE"] = keyfile.read()
            self.logger.info("Pulled the key successfully")
            return result
        except IOError as e:
            self.logger.exception("Key {} for provider {} could not be pulled".format(key_name, provider))
            self.logger.exception(e)
            return False

    def delete_key(self, provider, key_name):
        try:
            if provider == "aws" or provider == "openstack":
                os.remove("{}/{}/{}/{}".format(self.__root_path, self.__keys_dir, provider, key_name))
                self.logger.info("Successfully delete key {} for provider {}".format(key_name, provider))
                return True
        except OSError as e:
            self.logger.exception("Could not remove key {}".format(key_name))
            self.logger.exception(e)
            return False

    def deploy(self, data):
        try:
            provider = None
            if data["PROVIDER"] == "aws":
                provider = self.aws_prov
            elif data["PROVIDER"] == "openstack":
                provider = self.open_prov
            if provider:
                image = provider.get_image(data["IMAGE"])
                size = provider.get_size(data["SIZE"])
                networks = provider.get_networks(data["NETWORKS"])
                security_groups = provider.get_security_groups(data["SECURITY_GROUPS"])
                if ".pem" in data["KEY_NAME"]:
                    key_name = data["KEY_NAME"].split(".")[0]
                else:
                    key_name = data["KEY_NAME"]
                self.logger.info("""Deploying node for provider {} with the following options: Image {} size {} networks {} security groups {} and key {}""".format(data["PROVIDER"], image, size, networks, security_groups, key_name))
                if image and size:
                    self.logger.info("Size and image provided")
                    status = provider.create_node(data["NAME"], size, image, networks, security_groups, key_name)
                    if status:
                        self.logger.info("Deployed node {} successfully".format(data["NAME"]))
                        return True
            self.logger.info("Unable to deploy node {}".format(data["NAME"]))
            return False
        except Exception as e:
            self.logger.exception("Something bad happened")
            self.logger.exception(e)

    def deploy_options(self, data):
        result = {}
        if data["PROVIDER"] == "aws":
            provider = self.aws_prov
        elif data["PROVIDER"] == "openstack":
            provider = self.open_prov
        else:
            self.logger.info("Provider was not valid and so exiting")
            return False
        if provider is None:
            self.logger.info("No account has been set so exiting")
            return False
        if data["IMAGES"]:
            images = []
            image_objects = provider.list_images()
            for image in image_objects:
                images.append(str(image))
            result["IMAGES"] = images
        if data["SIZES"]:
            sizes = []
            size_objects = provider.list_sizes()
            for size in size_objects:
                sizes.append(str(size))
            result["SIZES"] = sizes
        if data["NETWORKS"]:
            networks = []
            network_objects = provider.list_networks()
            for net in network_objects:
                networks.append(str(net))
            result["NETWORKS"] = networks
        if data["SECURITY_GROUPS"]:
            security_groups = []
            security_objects = provider.list_security_groups()
            for sec_group in security_objects:
                security_groups.append(str(sec_group))
            result["SECURITY_GROUPS"] = security_groups

        self.logger.info("Deployment options to be sent {}".format(result))
        return result

    def delete_node(self, data):
        if data["PROVIDER"] == "aws":
            provider = self.aws_prov
        elif data["PROVIDER"] == "openstack":
            provider = self.open_prov
        else:
            self.logger.info("No valid provider provided")
            return False
        if provider is None:
            self.logger.info("Provider is not set so exiting")
            return False
        if data["NODE_ID"]:
            node = provider.get_node(id=data["NODE_ID"])
            provider.destroy_node(node)
            self.logger.info("Deleted node {} for provider {}".format(data["NODE_ID"], data["PROVIDER"]))
        elif data["NODE_NAME"]:
            node = provider.get_node(name=data["NODE_NAME"])
            provider.destroy_node(node)
            self.logger.info("Deleted node {} for provider {}".format(data["NODE_NAME"], data["PROVIDER"]))
        else:
            self.logger.info("No node name or node id provided exiting")
            return False
        return True

    def add_record(self, data):
        try:
            # Convert to dict
            disk_info = data["DISK_USAGE"]
            del data["DISK_USAGE"]
            # Put data into mongoDB
            instance_post_id = self.inst_use.insert_one(data).inserted_id
            vol_post_id = self.vols.insert_one(disk_info).inserted_id
            self.logger.info("Added a record to the db")
            return instance_post_id
        except pymongo.errors.ConnectionFailure as e:
            self.logger.exception("Could not access the MongoDB")
            self.logger.exception(e)
            return False
        except Exception as e:
            self.logger.exception("Something went wrong")
            self.logger.exception(e)
            return False

    def get_current_data(self):
        datetime.datetime.today()
        query_use = {"DATE_TIME": {"$gte": (datetime.datetime.now() - datetime.timedelta(minutes=70))}} # Accounting for UTC
        self.logger.info(query_use)
        provider_query = {}
        info_df = pd.DataFrame(list(self.inst_info.find(provider_query)))
        usage_df = pd.DataFrame(list(self.inst_use.find(query_use)))
        vol_df = pd.DataFrame(list(self.vols.find(query_use)))

        self.logger.info("Records for instances: {}".format(info_df.count()))
        self.logger.info("Records of instance usages: {}".format(usage_df.count()))
        try:
            all_df = pd.merge(info_df, usage_df, on=["INSTANCE_ID", "PROVIDER"], how="right")
        except KeyError as e:
            self.logger.exception("Appears there is no data being collected currently")
            self.logger.exception(e)
            return []

        # Get the network usage in MB
        all_df["NETWORK_USAGE"] = all_df.apply(lambda row: (row["BYTES_RECV"] + row["BYTES_SENT"]) / 1048576, axis=1)
        all_df["MEMORY_USAGE"] = all_df.apply(lambda row: (row["MEM_AVAIL"] / row["MEM_TOTAL"]), axis=1)
        all_df["MEMORY_TOTAL"] = all_df.apply(lambda row: row["MEM_TOTAL"] / 1073741824, axis=1)

        # Do the costings
        size_prices = []
        for size, provider in zip(all_df["SIZE"], all_df["PROVIDER"]):
            if provider == "aws":
                if self.aws_prov:
                    size_obj = self.aws_prov.get_size(size)
                    size_prices.append(size_obj.price)
                else:
                    size_prices.append(0)
            elif provider == "openstack":
                if self.open_prov:
                    size_obj = self.open_prov.get_size(size)
                    size_prices.append(size_obj.price)
                else:
                    size_prices.append(0)

        all_df["COST"] = size_prices
        return all_df[["DATE_TIME", "INSTANCE_ID", "INSTANCE_NAME", "PROVIDER", "CPU_USAGE",
                       "MEMORY_USAGE", "MEMORY_TOTAL", "NETWORK_USAGE", "CONNECTIONS", "COST"]].to_json()

    def get_specific_data(self, year, month=None, day=None):
        year_overall = False
        month_overall = False
        if month is None:
            year_overall = True
            month = 1
        if day is None:
            month_overall = True
            day = 1

        year = int(year)
        month = int(month)
        day = int(day)

        self.logger.info("Date to work with {}-{}-{}".format(year, month, day))

        search_date = datetime.datetime(year, month, day)
        if year_overall:
            self.logger.info("Working with year overall data")
            end_date = datetime.datetime(year + 1, month, day)
            id_field = {"INSTANCE_ID": "$INSTANCE_ID", "DATE_TIME": {"$month": "$DATE_TIME"}}
        elif month_overall:
            self.logger.info("Working with month overall data")
            end_date = datetime.datetime(year, month + 1, day)
            id_field = {"INSTANCE_ID": "$INSTANCE_ID", "DATE_TIME": {"$dayOfMonth": "$DATE_TIME"}}
        else:
            self.logger.info("Working with daily data")
            end_date = datetime.datetime(year, month, day + 1)
            id_field = {"INSTANCE_ID": "$INSTANCE_ID", "DATE_TIME": {"$hour": "$DATE_TIME"}}

        pipeline = [
            {
                "$match": {
                    "DATE_TIME": {
                        "$gte": search_date,
                        "$lt": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": id_field,
                    "RECORDS": {"$sum": 1},
                    "CPU_USAGE": {"$avg": "$CPU_USAGE"},
                    "MEM_AVAIL": {"$avg": "$MEM_AVAIL"},
                    "MEM_TOTAL": {"$max": "$MEM_TOTAL"},
                    "CONNECTIONS": {"$avg": "$CONNECTIONS"},
                    "PACKETS_RECV": {"$avg": "$PACKETS_RECV"},
                    "PACKETS_SENT": {"$avg": "$PACKETS_SENT"},
                    "BYTES_SENT": {"$avg": "$BYTES_SENT"},
                    "BYTES_RECV": {"$avg": "$BYTES_RECV"}
                }
            },
        ]

        query_use = {"DATE_TIME": {"$lt": end_date, "$gt": search_date}}
        info_df = pd.DataFrame(list(self.inst_info.find()))
        usage_df = pd.DataFrame(list(self.inst_use.aggregate(pipeline)))
        vol_df = pd.DataFrame(list(self.vols.find(query_use)))

        self.logger.info("Records for instances: {}".format(info_df.count()))
        self.logger.info("Records of instance usages: {}".format(usage_df.count()))
        try:
            usage_df = self.__unpack(usage_df, "_id")
            all_df = pd.merge(info_df, usage_df, on="INSTANCE_ID", how="right")
        except KeyError as e:
            self.logger.exception("Appears there is no data being collected currently")
            self.logger.exception(e)
            return []

        self.logger.info("Joined the instance and usage info")
        # Get the network usage in MB
        all_df["NETWORK_USAGE"] = all_df.apply(lambda row: (row["BYTES_RECV"] + row["BYTES_SENT"]) / 1048576, axis=1)
        all_df["MEMORY_USAGE"] = all_df.apply(lambda row: (row["MEM_AVAIL"] / row["MEM_TOTAL"]), axis=1)
        all_df["MEMORY_TOTAL"] = all_df.apply(lambda row: row["MEM_TOTAL"] / 1073741824, axis=1)

        self.logger.info("Setup the Usages so that they are in easier amounts to deal with")

        # Do the costings
        size_prices = []
        for size, provider in zip(all_df["SIZE"], all_df["PROVIDER"]):
            if provider == "aws":
                size_obj = self.aws_prov.get_size(size)
                self.logger.info("Working with size {}".format(size_obj))
                size_prices.append(size_obj.price)
                self.logger.info("Working with price {}".format(size_obj.price))
            elif provider == "openstack":
                size_obj = self.open_prov.get_size(size)
                self.logger.info("Working with size {}".format(size_obj))
                size_prices.append(size_obj.price)
                self.logger.info("Working with price {}".format(size_obj.price))

        self.logger.info("Dealt with costings, costs: {}".format(size_prices))

        full_cost = [((cost/(60/5)) * records) for cost, records in zip(size_prices, all_df["RECORDS"])]

        all_df["COST"] = full_cost

        return all_df[["DATE_TIME", "INSTANCE_ID", "INSTANCE_NAME", "PROVIDER", "CPU_USAGE",
                       "MEMORY_USAGE", "MEMORY_TOTAL", "NETWORK_USAGE", "CONNECTIONS", "COST"]].to_json()

    def __unpack(self, df, column, fillna=None):
        ret = None
        if fillna is None:
            ret = pd.concat([df, pd.DataFrame((d for idx, d in df[column].iteritems()))], axis=1)
            del ret[column]
        else:
            ret = pd.concat([df, pd.DataFrame((d for idx, d in df[column].iteritems())).fillna(fillna)], axis=1)
            del ret[column]
        return ret

    def get_dates(self):
        old_year = datetime.datetime.today().year
        new_year = datetime.datetime.today().year
        cursor = self.inst_use.find({}).sort([("DATE_TIME", 1)]).limit(1)
        if cursor.count() > 0:
            self.logger.info(cursor.count())
            for result in cursor:
                self.logger.info(result["DATE_TIME"])
                date = datetime.datetime.strptime(result["DATE_TIME"], "%Y-%m-%d %H:%M:%S")
                old_year = date.year
        else:
            old_year = datetime.datetime.now().year

        cursor = self.inst_use.find({}).sort([("DATE_TIME", -1)]).limit(1)
        if cursor.count() > 0:
            self.logger.info(cursor.count())
            for result in cursor:
                self.logger.info(result["DATE_TIME"])
                date = datetime.datetime.strptime(result["DATE_TIME"], "%Y-%m-%d %H:%M:%S")
                new_year = date.year
        else:
            new_year = datetime.datetime.now().year

        if old_year != new_year:
            years = range(old_year, new_year + 1)
        else:
            years = [old_year]

        self.logger.info("Years for results {}".format(years))

        months = {"Janurary": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                  "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

        return years, months

    def get_days(self, month, year):
        if month in [1, 3, 5, 7, 8, 10, 12]:
            days = 31
        elif month in [4, 6, 9, 11]:
            days = 30
        elif year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            days = 29
        else:
            days = 28
        return days
