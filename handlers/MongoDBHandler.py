from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MONGODB_URI, SPF_DATABASE

class MongoDBHandler():
    def __init__(self, collection_name):

        self.client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

        self.db = self.client[SPF_DATABASE]
        self.collection = self.db[collection_name]

    def get_collection(self):
        return self.collection
    
    def insert_data(self, data):
        self.collection.insert_one(data)


    def read_data(self, query=None, sort=None, limit=None):
        if query:
            data = self.collection.find(query)
        else:
            data = self.collection.find()

        if sort:
            data = data.sort(sort)

        if limit:
            data = data.limit(limit)

        data_list = list(data)
        return data_list
    
    def update_data(self, query, data):
        update_query = {"$set": data}
        try:
            self.collection.update_one(query, update_query)
        except Exception as ex:
            raise ex

    def delete_data(self, data):
        self.collection.delete_one(data)
    
    def create_index(self, field):
        self.collection.create_index(field, unique=True)
    
    def close_connection(self):
        self.client.close()