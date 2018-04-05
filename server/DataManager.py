from pymongo import MongoClient
import pymongo.errors
import json
import pandas as pd
import datetime
import os
from accounts.OpenStack import OpenStack
from accounts.AWS import AWS


class DataManager:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client["cloud-fyp"]
        self.inst_info = self.db["instances"]
        self.inst_use = self.db["instance_usages"]
        self.vols = self.db["volumes"]
        self.accounts = self.db["accounts"]
        self.__root_path = self.__get_root_path()
        self.__keys_dir = "keys"
        aws_account = self.get_set_account("AWS")
        open_account = self.get_set_account("OPENSTACK")
        self.aws_prov = AWS(aws_account["ACCOUNT_ID"], aws_account["ACCOUNT_SECRET_KEY"], aws_account["ACCOUNT_REGION"])
        self.open_prov = OpenStack(open_account["ACCOUNT_ID"], open_account["ACCOUNT_PASSWORD"],
                                   open_account["ACCOUNT_AUTH_URL"], open_account["ACCOUNT_AUTH_VERSION"],
                                   open_account["ACCOUNT_TENANT_NAME"], open_account["ACCOUNT_IMAGE_VERSION"])

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
                return True
            return False
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
            return False

    def get_accounts(self, provider=None):
        try:
            if provider:
                accounts = []
                for document in self.accounts.find({"PROVIDER": provider}, {'_id': False}):
                    accounts.append(document)
                return accounts
            else:
                return list(self.accounts.find({}, {'_id': False}))
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
            return False

    def set_account(self, account_name, provider):
        try:
            result_unset = self.accounts.update_one({"PROVIDER": provider, "SET_ACCOUNT": True}, {"$set": {"SET_ACCOUNT": False}})
            result_set = self.accounts.update_one({"ACCOUNT_NAME": account_name, "PROVIDER": provider}, {"$set": {"SET_ACCOUNT": True}})
            if result_set.modified_count > 0 and (result_unset.matched_count > 0 and result_unset.modified_count > 0) or result_unset.matched_count == 0:
                return True
            return False
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
            return False

    def get_set_account(self, provider):
        try:
            set_account = self.accounts.find_one({"PROVIDER": provider, "SET_ACCOUNT": True}, {'_id': False})
            return set_account
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
            return False

    def delete_account(self, account_name, provider):
        try:
            delete_account = self.accounts.delete_one({"PROVIDER": provider, "ACCOUNT_NAME": account_name})
            if delete_account.deleted_count > 0:
                return True
            return False
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(e)
            return False

    def add_key(self, data):
        try:
            with open("{}/{}/{}/{}".format(self.__root_path,
                                           self.__keys_dir,
                                           data["PROVIDER"],
                                           data["KEY_NAME"]), "w") as key_file:
                key_file.write(data["KEY_VALUE"])
        except Exception as e:
            print(e)
            return False
        return True

    def get_keys(self, provider):
        if provider == "aws" or provider == "openstack":
            return os.listdir("{}/{}/{}/".format(self.__root_path, self.__keys_dir, provider))
        return []

    def download_key(self, provider, key_name):
        try:
            result = {
                "KEY_NAME": key_name,
                "KEY_VALUE": ""
            }
            with open("{}/{}/{}/{}".format(self.__root_path, self.__keys_dir, provider, key_name), "r") as keyfile:
                result["KEY_VALUE"] = keyfile.read()
            return result
        except IOError as e:
            return False

    def delete_key(self, provider, key_name):
        try:
            if provider == "aws" or provider == "openstack":
                os.remove("{}/{}/{}/{}".format(self.__root_path, self.__keys_dir, provider, key_name))
                return True
        except OSError as e:
            print(e)
            return False

    def deploy(self, data):
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
            if image and size:
                provider.deploy_node_script(data["NAME"], size, image, networks, security_groups, True)
                return True
        return False

    def deploy_options(self, data):
        result = {}
        if data["PROVIDER"] == "aws":
            provider = self.aws_prov
        elif data["PROVIDER"] == "openstack":
            provider = self.open_prov
        else:
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
        return result

    def add_record(self, post_body):
        try:
            # Convert to dict
            instance_info = json.loads(post_body)
            disk_info = instance_info["DISK_USAGE"]
            del instance_info["DISK_USAGE"]
            # Put data into mongoDB
            instance_post_id = self.inst_use.insert_one(instance_info).inserted_id
            vol_post_id = self.vols.insert_one(disk_info).inserted_id
            return instance_post_id
        except pymongo.errors.ServerSelectionTimeoutError as e:
            return False

    def get_current_data(self):
        datetime.datetime.today()
        query_use = {"DATE_TIME": {"$lt": datetime.datetime.now(),
                                   "$gt": datetime.datetime.now() - datetime.timedelta(minutes=5)}
                     }
        print(query_use)
        provider_query = {}
        info_df = pd.DataFrame(list(self.inst_info.find(provider_query)))
        usage_df = pd.DataFrame(list(self.inst_use.find(query_use)))
        vol_df = pd.DataFrame(list(self.vols.find(query_use)))

        print(info_df)
        print(usage_df)

        all_df = pd.merge(info_df, usage_df, on="ASSIGNED_ID", how="right")

        # Get the network usage in MB
        all_df["NETWORK_USAGE"] = all_df.apply(lambda row: (row["BYTES_RECV"] + row["BYTES_SENT"]) / 1048576, axis=1)
        all_df["MEMORY_USAGE"] = all_df.apply(lambda row: (row["MEM_AVAIL"] / row["MEM_TOTAL"]), axis=1)
        all_df["MEMORY_TOTAL"] = all_df.apply(lambda row: row["MEM_TOTAL"] / 1073741824, axis=1)

        return all_df[["TIMESTAMP", "INSTANCE_ID", "INSTANCE_NAME", "PROVIDER", "CPU_USAGE",
                       "MEMORY_USAGE", "MEMORY_TOTAL", "NETWORK_USAGE", "CONNECTIONS"]].to_json()

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

        search_date = datetime.datetime(year, month, day)
        if year_overall:
            end_date = datetime.datetime(year + 1, month, day)
            id_field = {"ASSIGNED_ID": "$ASSIGNED_ID", "DATE_TIME": {"$month": "$DATE_TIME"}}
        elif month_overall:
            end_date = datetime.datetime(year, month + 1, day)
            id_field = {"ASSIGNED_ID": "$ASSIGNED_ID", "DATE_TIME": {"$dayOfMonth": "$DATE_TIME"}}
        else:
            end_date = datetime.datetime(year, month, day + 1)
            id_field = {"ASSIGNED_ID": "$ASSIGNED_ID", "DATE_TIME": {"$hour": "$DATE_TIME"}}

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

        # TODO: Do more to manage the case where there is no data.
        if usage_df.size == 0:
            return []

        usage_df = self.__unpack(usage_df, "_id")

        # TODO: if year_overall, merge the months, if month merge the days, if day just leave it?

        all_df = pd.merge(info_df, usage_df, on="ASSIGNED_ID", how="right")

        # Get the network usage in MB
        all_df["NETWORK_USAGE"] = all_df.apply(lambda row: (row["BYTES_RECV"] + row["BYTES_SENT"]) / 1048576, axis=1)
        all_df["MEMORY_USAGE"] = all_df.apply(lambda row: (row["MEM_AVAIL"] / row["MEM_TOTAL"]), axis=1)
        all_df["MEMORY_TOTAL"] = all_df.apply(lambda row: row["MEM_TOTAL"] / 1073741824, axis=1)

        return all_df[["DATE_TIME", "INSTANCE_ID", "INSTANCE_NAME", "PROVIDER", "CPU_USAGE",
                       "MEMORY_USAGE", "MEMORY_TOTAL", "NETWORK_USAGE", "CONNECTIONS"]].to_json()

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
        for result in cursor:
            old_year = result["DATE_TIME"].year

        cursor = self.inst_use.find({}).sort([("DATE_TIME", -1)]).limit(1)
        for result in cursor:
            new_year = result["DATE_TIME"].year

        if old_year != new_year:
            years = range(old_year, new_year + 1)
        else:
            years = [old_year]

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
