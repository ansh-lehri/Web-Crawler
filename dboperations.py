# includes methods to query mongodb databases.


# importing python packages
from pymongo import MongoClient
from pprint import pprint

# importing from user-developed module
from dbconnections import DbConnections

class MongoDB:

    def __init__(self, db_name):

        # instantiating and establishing connection with database
        mongodb_open = DbConnections(db_name)
        self.db = mongodb_open.client[db_name]
        

    
    def create_doc(self, data, coll):
        """ insert data in given collection """
        collection = self.db[coll]
        try:
            collection.insert_one(data)
            return True
        except Exception as e:
            pprint("Mongodb exception:", e)
            return False


    
    def fetch_doc(self, link, coll):
        """ returns document with given link as _id """
        collection = self.db[coll]
        try:
            data = collection.find_one({"_id": link})
            if data:
                return data
            return False
        except Exception as e:
            print(e)
            return False
    



    def check_doc(self, link, coll):
        """ returns document with given link as _id """
        collection = self.db[coll]
        try:
            data = collection.find_one({"_id": link})
            if data:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False



    def delete_coll_data(self, colls: list):
        """ delete all data in the collections passed in colls list """
        for coll in colls:
            collection = self.db[coll]
            try:
                collection.delete_many({})
                print("Deleted everything in %s" % (coll))
            except Exception as e:
                print(e)




    def delete_single_doc(self, coll_name, doc):
        # delete single document passed as doc in the collection
        # passed in coll_name

        collection = self.db[coll_name]
        try:
            collection.delete_one(doc)
            print("Deleted the doc")
        except Exception as e:
            print(e)


    
    def fetch_random_doc(self, coll_name, number_of_docs):
        # fetches random number of documents from collection passed in coll_name
        # Number of documents to be fetched is passed in number_of_docs

        collection = self.db[coll_name]
        try:
            docs=collection.aggregate([{"$match":{"parsed":"False"}}, {"$sample":{"size":number_of_docs}}])
            #parse_doc = {"_id":docs["_id"],"data":docs["file_data"]}
            return docs          
        except Exception as e:
            print(e)
            return ""

    



    def fetch_random_docs_not_crawled(self, coll_name, number_of_docs):


        collection = self.db[coll_name]
        try:
            docs = collection.aggregate([{"$sample":{"size":number_of_docs}}])
            return docs
        except Exception as e:
            print(e)
            return ""




    
    def update_doc(self, coll_name, ids):
        # updates document present in collection passed as coll_name with document
        # id as ids


        collection = self.db[coll_name]
        try:
            collection.update_one({'_id':ids},{"$set":{"parsed":"True"}})
        except Exception as e:
            print(e)
            

