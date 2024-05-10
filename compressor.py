# include methods to create document with required filed types, insert documents
# passed into mongodb databases within proper collections, read files from 
# local directory and a method called wait to do nothing. 


# import python built-in libraries and installed packages.
import os.path
import re
from bs4 import BeautifulSoup,SoupStrainer
from bson import Binary
from pprint import pprint


# import from user-developed module.
from dboperations import MongoDB



class Compressor:


    def __init__(self):

        self.only_html = SoupStrainer("html")
        self.path = "/tmp"




    # inserts data passed into appropriate collection .
    async def insert_mongodb_doc(self, collection, data, mongodb):
        try:
            if mongodb.create_doc(coll=collection, data=data):
                print("Insertion successful into db")
            else:
                print("Insertion failed")
        except Exception as e:
            print("Error: ",e)
        



    async def create_mongodb_doc(self, doc, mime_type, extension, mongodb_doc_id, mongodb):
        
        # mongodb document is created with required fields.
        soup = BeautifulSoup(doc,'html.parser',parse_only=self.only_html)
        try:
            url = soup.singularity['href']
        except Exception as e:
            print(e)
            return
        
        
        data = {
            '_id': mongodb_doc_id,
            # TODO file_type to select dynamically
            'mime_type': mime_type,
            'url': url,
            'file_extension': extension,
            'file_data': Binary(bytes(doc,"utf-8")),
            'parsed': "False",
        }
 
        await self.insert_mongodb_doc("https3",data, mongodb)

    


    async def read_file(self,compressor_doc_id, extension):

        # reads file from disk.
        
        file = open(os.path.join(self.path,"Singularity"+f"{compressor_doc_id}"+"."+extension),'r+',encoding='utf-8')
        doc = file.read()
        file.close()
        print("File Created and Saved")
        return doc



    # does nothing. Made with intent to skip the chance of the task in the event loop.
    async def wait(self):
        pass
