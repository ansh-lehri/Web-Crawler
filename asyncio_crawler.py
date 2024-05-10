# asyncio_crawler controls the crawler written to crawl the web.
# It uses asynchronization programming. 

# import bulit-in libraries

import asyncio
import os
import queue
import random
import re
import time
from aiologger import Logger
from random import shuffle

# import user-developed modules

from crawler import Scraper
from dboperations import MongoDB
from compressor import Compressor
from server import Server
from parse import Parser
from proxy_server import Proxy

# initiate server object.
server = Server()
# initiate parser object.
parsers = Parser()

# initiate scraper object.
scrape = Scraper()

# initiate compressor object.
compressor = Compressor()

# creates a connection pool to Server database.
server_mongodb = MongoDB(db_name='Server')

# creates a connection pool to Compressor database.
compressor_mongodb = MongoDB(db_name='Compressor')


# counter and document id  variables initial values.
crawler_doc_id = 0
count_crawler = 0
compressor_doc_id = 0
mongodb_doc_id = 0
#doc_id = 0

# path of local directory where crawler writes downloded files.
path = "/tmp"

async def start_cycle(server_crawler_queue):

    urls = []
    
    # fetch_random_doc method fetches 50 random urls from Not Crawled collection
    # of compressor database.
    cursor = compressor_mongodb.fetch_random_docs_not_crawled(coll_name="Not Crawled", number_of_docs=18)
    
    # iterate the cursor object and push the urls into urls list
    for doc in cursor:
        urls.append(doc['_id'])

    # insert a tuple of url and Yes into server_crawler_queue. url gives the link
    # of which web page is to be stored and Yes indicates that this url is taken from
    # Not Crawled collection of database and if crawled, should be deleted.

    for url in urls:
        await server_crawler_queue.put((url,"Yes"))


async def compress(compressor_queue: asyncio.Queue):
    
    while True:
        # checks if any web page has been downloaded. If not, the task waits for its
        # turn in the loop.
        global compressor_doc_id
        if os.path.getsize(path)==0 or compressor_doc_id > crawler_doc_id:
            await compressor.wait()
        
        # acting as consumer, fetch tuple from the queue. All the tuple elements
        # are explained in web_page_downloader method below.
        
        url, page_status, content_type, extension = await compressor_queue.get()
        print(compressor_queue.qsize())

        if page_status=="200":
            
            # Web page document id to be used as document identifier for the local directory.
            #global compressor_doc_id
            compressor_doc_id+=1

            # 'read_file' method  reads corresponding web page from the local directory.
            doc = await compressor.read_file(compressor_doc_id,extension)

            # Web page Id to be used as _id in MongoDb.
            global mongodb_doc_id
            mongodb_doc_id+=1

        # for specifications of  'create_mongodb_doc', 'insert_mongodb_doc' methods, refer compressor module.

            await compressor.create_mongodb_doc(doc, content_type, extension, mongodb_doc_id, compressor_mongodb)
            
        elif page_status=="404":
            await compressor.insert_mongodb_doc("Not Crawled", {'_id':url}, compressor_mongodb)
           
        elif page_status=="100":
            await compressor.insert_mongodb_doc("Not Text", {'url':url, 'content_type':content_type}, compressor_mongodb)  
         
        #return ""
        # Compressor task recursively calls itself.
        #await compress(compressor_queue)




async def web_page_downloader(server_crawler_queue: asyncio.Queue, compressor_queue: asyncio.Queue, proxy_pool: list):
    
    while True:
     
        global count_crawler
        count_crawler+=1
        # shuffle the server_crawler_queue everytime a task fetches from the queue
        # shuffle helps to curb the requests blocking problem and tries to impart
        # randomness to some extent.

        shuffle(server_crawler_queue._queue)

        # url ====> web page to download, to_delete ====> signal whether to delete the url
     
        url, to_delete = await server_crawler_queue.get()  
        
        # index to pass the corresponding proxy to uel page requests.

        index = random.randint(1,len(proxy_pool))
        index-=1
        print(index)

        # calling server_crawler_buffer method to download the web page 
        # resut ====> successful if url request executed else unsuccessful
        # request ====> request object of url request
        # ext ====> type of web page, html/htm/xml etc.
        # content_type ====> mime type of web page
        # page_status =====> 1. 200 = page exists.
        #                    2. 404 = either page not exists or request blocked by website.
        #                    3. 100 = schema of mime type != text

        result, request, ext, content_type, page_status = await scrape.server_crawler_buffer(url, proxy_pool[index], to_delete)

        if page_status=="200":

            # if url is to be deleted call 'delete_single_doc' method from dboperations module
            # coll_name = collection name, doc = url to delete.

            if to_delete=="Yes":
                compressor_mongodb.delete_single_doc(coll_name="Not Crawled", doc={'_id':url})
            global crawler_doc_id
            crawler_doc_id+=1
            
            # open_file method called to write the web page in a file.
            await scrape.open_file(request, crawler_doc_id, ext, url)

        # tuple is passed into the compressor_queue in the next 5 statements according
        # to conditions. Compressor_queue tuple indicates the collection in which url is 
        # to be inserted. Content_type being one of the field type of collection https along
        # with url. 
        # To see schema of collections of each database, refer dboperations module. 
        # acts as producer for compressor_queue.

            await compressor_queue.put(("", page_status, content_type, ext))
        elif page_status=="404":
            await compressor_queue.put((url, page_status, "", ext))
        elif page_status=="100":
            await compressor_queue.put((url, page_status, content_type, ext))

        #return ""
        # web_page_downloader task recursively calls itself.
        #await web_page_downloader(server_crawler_queue,compressor_queue, proxy_pool)




async def serve(parser_server_queue: asyncio.Queue, server_crawler_queue: asyncio.Queue):

    # server being consumer in parser-server linkage, 
    # consumes url from the queue.
    while True:
        url = await parser_server_queue.get()

        # handle_urls method is called to check if the url is already crawled or not.
        # answer = YES ====> Not Crawled
        # answer = NO =====> Already Crawled

        answer = await server.handle_urls(url, server_mongodb)
        parser_server_queue.task_done()
        print(answer)
        if answer=="YES":
            
            # insert tuple into the server_crawler_queue. 
            # first entry is url to crawl, second entry to show if the url is to be 
            # deleted from "Not Crawled" collection of compressor database.
            # if No ====> Do not delete, Yes ====> Delete
            # every server task will insert No into the queue as these urls are not
            # present in "Not Crawled" collection and are fresh urls and not the ones 
            # giving 404 due to blocking of requests.

            await server_crawler_queue.put((url,"No"))
            
        #return ""    
        # server task recursively calls itself.
        await asyncio.sleep(15)
        #await serve(parser_server_queue, server_crawler_queue)




async def parse(parser_server_queue: asyncio.Queue):
    
    # each parse task waits for 10 seconds to get https collection of 
    # compressor database filled to avoid consumer problem.


    # 'read_file' method of parser is called to read and parse a web page
    # parser acts as producer of urls in parser-server linkage
    #await asyncio.sleep(15)
    while True:
        
        result = await parsers.read_file(parser_server_queue, compressor_mongodb)

        # if no web page is found in database, task returns "" as result
        #if result=="Kill the Task":
        #    return ""
        print(result)
        #return ""
        # succesfully executed parse tasks call themselves recursively.
        await asyncio.sleep(20)
        #await parse(parser_server_queue)




async def main():
    
    # initializing asyncio Queues for pipelines between Parser-Server, 
    # Server-Crawler, Crawler-Compressor in sequence below:

    parser_server_queue = asyncio.Queue()   
    server_crawler_queue = asyncio.Queue()
    compressor_queue = asyncio.Queue()

    # creating proxy_pool to introduce proxy rotation.
    # not working for now because proxies need to be premium ones.

    proxy = Proxy()
    proxy_pool = proxy.proxy_pool

    # initializing parsers, servers, crawlers and compressors in sequence to
    # store the tasks created.

    parsers = []
    servers = []
    crawlers = []
    compressors = []

    # instantializing tasks for crawler, compressor, parser and server.
    # cycle of operation is as follows:
    # Crawler ----> Compressor ----> Parser ----> Server ----> Crawler
    # creating tasks, starts the process itself.
    
    for _ in range(50):
        crawlers.append(asyncio.create_task(web_page_downloader(server_crawler_queue,compressor_queue,proxy_pool)))
    for _ in range(40):
        compressors.append(asyncio.create_task(compress(compressor_queue)))
    for _ in range(5):
        parsers.append(asyncio.create_task(parse(parser_server_queue)))
    for _ in range(10):
        servers.append(asyncio.create_task(serve(parser_server_queue,server_crawler_queue)))



    await start_cycle(server_crawler_queue)

    time.sleep(20)

    # queues are joined to wait for every task get cancelled and return.
    # ideally no task should return as the circle will run infinitely or until
    # terminated.
    
    await server_crawler_queue.join()
    await compressor_queue.join()
    await parser_server_queue.join()



if __name__=="__main__":

    server_mongodb.delete_coll_data(colls=["https"])
    compressor_mongodb.delete_coll_data(colls=['https3'])


    # run the main thread.
    asyncio.run(main())
