from pymongo import MongoClient
import json
import pandas as pd
import datetime


class DataManager:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client["cloud-fyp"]
        self.inst_info = self.db["instances"]
        self.inst_use = self.db["instance_usages"]
        self.vols = self.db["volumes"]

    def add_record(self, post_body):
        # Convert to dict
        instance_info = json.loads(post_body)
        # Put data into mongoDB
        post_id = self.inst_use.insert_one(instance_info).inserted_id
        return post_id

    def get_current_data(self, CLI):
        datetime.datetime.today()
        query_use = {"DATE_TIME": {"$lt": datetime.datetime.now(),
                                   "$gt": datetime.datetime.now() - datetime.timedelta(minutes=5)}}
        info_df = pd.DataFrame(list(self.inst_info.find()))
        usage_df = pd.DataFrame(list(self.inst_use.find(query_use)))
        vol_df = pd.DataFrame(list(self.vols.find(query_use)))

        all_df = pd.merge(info_df, usage_df, on="ASSIGNED_ID", how="right")

        # Get the network usage in MB
        all_df["NETWORK_USAGE"] = all_df.apply(lambda row: (row["BYTES_RECV"] + row["BYTES_SENT"]) / 1048576, axis=1)
        all_df["MEMORY_USAGE"] = all_df.apply(lambda row: (row["MEM_AVAIL"] / row["MEM_TOTAL"]), axis=1)
        all_df["MEMORY_TOTAL"] = all_df.apply(lambda row: row["MEM_TOTAL"] / 1073741824, axis=1)

        if not CLI:
            return all_df[["TIMESTAMP", "INSTANCE_ID", "INSTANCE_NAME", "PROVIDER", "CPU_USAGE",
                           "MEMORY_USAGE", "MEMORY_TOTAL", "NETWORK_USAGE", "CONNECTIONS"]].to_json()

    def get_specific_data(self, CLI, year, month, day):
        year_overall = False
        month_overall = False
        if month is None:
            year_overall = True
            month = 1
        if day is None:
            month_overall = True
            day = 1

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

        if not CLI:
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
