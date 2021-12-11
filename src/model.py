from typing import Dict
import pymongo as mongo
import config


class MongoDB:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        self.client = mongo.MongoClient(conn_string)
        self.db_name = self.client[config.main_config["db_config"]["db_name"]]
        self.collection = self.db_name[
            config.main_config["db_config"]["collection_name"]
        ]

    def update_server_status(self, server_ip: str, update_value: Dict):
        """Update status

        Dethrone the score of this server and and assign score to another servers
        It will be 0/1 value for know, 0 as service is down in this machine
        and 1 as service is up in this machine.
        """
        find_obj = {"ip": server_ip}
        update_status_result = self.collection.update_one(
            find_obj, {"$set": update_value}
        )

        return 1 if update_status_result.modified_count == 1 else 0

    def find_obj(self, key, value):
        return self.collection.find_one({key: value})

    def get_statuses(self, server: str, status_type: str, value: int):
        """Status function
        server_status or service_status
        """
        return self.collection.find_one({"ip": server, status_type: value})

    def init_server_document(self, server_document_initiation: Dict):
        """Init server document
        It will insert one document with this key: value :
        {
            ip: string, which server is our target
            server_status: Int32 only for know server is down or up with getting ping of this servers, is up or down?
            service_status: Int32 only for checking a service is Running or Stopped
            date_time: Int32 a time for know when this server updated this document
        }
        """
        init_document_result = self.collection.insert_one(server_document_initiation)
        return init_document_result.inserted_id
