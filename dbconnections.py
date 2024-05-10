# central file to create connection pool for Server and Compressor database which 
# every process of crawler can use.

from pymongo import MongoClient
from pprint import pprint


class DbConnections:

    def __init__(self, db_name):
        """ connect to database """
        try:
            self.client = MongoClient(
                "mongodb+srv://<username>:<pwd>@cluster0.tdevi.mongodb.net/%s?retryWrites=true&w=majority" % (
                    db_name)
            )
            print("Connection established to online mongodb.")

        except Exception as e:
            print(e)
            print("Online db not available. Connecting to local mongodb")
            self.client = MongoClient()

    
