from typing import Dict
import pymongo as mongo
import config


class MongoDB:
    def __init__(self, connString: str):
        self.connString = connString
        self.client = mongo.MongoClient(connString)
        self.db = self.client[config.main_config["db"]["db_name"]]
        self.collection = self.db[config.main_config["db"]["collection_name"]]

    def update_server_status(self):
        """Update status
        It will be 0/1 value for know, 0 as service is down in this machine
        and 1 as service is up in this machine.
        """

    def get_statuses(self, server: str, status_type: str, value: int):
        """Status function
        server_status or service_status
        """
        self.collection.find_one({"ip": server, status_type: value})

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
        self.collection.insert_one(server_document_initiation)
