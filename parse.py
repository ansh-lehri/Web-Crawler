# includes methods to read web page stored in database and parse them to extract
# anchor tags and convert them from relative to absolute.

# importing built-in libraries and python packages.

import asyncio
import os.path
import re
import threading
import time
from bs4 import BeautifulSoup,SoupStrainer
from urllib.parse import urljoin
from urllib.parse import urldefrag
from urllib.parse import urlparse
from urllib.parse import unquote


class Parser:

    def __init__(self):
        
        # tells BeautifulSoup parser to parse only html section of the page
        self.only_html = SoupStrainer("html")




    async def extract_tags(self, doc):

        soup = BeautifulSoup(doc, "html.parser")
        a_tags = soup.find_all("a")

        # Getting the original url of the current page
        soup = BeautifulSoup(doc,'html.parser',parse_only=self.only_html)

        # singularity tag created in every html file is used to extract original
        # url. Meta-tags could have been used but not all pages used meta-tag to 
        # write original url. 

        base_url = soup.singularity['href']
        if base_url==None:
            base_url=""
        
        return base_url, a_tags


    def is_absolute(self, url):
        absolute = bool(urlparse(url).netloc)
        return absolute


    async def correct_url_structure(self, urls):
        
        try:
            return re.sub(r"\/[(a-zA-Z_)]+(?=\:).*|[?#].*", " ", urls)
        except Exception as e:
            return




    async def read_file(self, parser_server_queue, mongodb):

       # reads one document from the database at random.
       # if error is raised, returns.
        try:
            cursor = mongodb.fetch_random_doc('https3',1)
            for docs in cursor:
                doc = docs['file_data']
                ids = docs['_id']
            mongodb.update_doc('https3',ids)
            
        except Exception as e:
            return "Kill the Task"
        
        # extract_tags return list of all 'a' tags and url of the page parsed.
        # base_url ====> page url, a_tags ====> list of 'a' tags.
        base_url, a_tags = await self.extract_tags(doc)
        
        if base_url == "":
            return

        
        for url in a_tags:

            urls = url.get("href")
            if urls==None:
                return
            

            # check if link retrieved is in absolute form. 
            # If False, convert to absolute and then check the structure of url formed. 
            # If True, directly check the structure of url formed.
            # While checking structure, anything beyond and including [#,?,=,:] must be dropped.


            if self.is_absolute(urls):
                urls = await self.correct_url_structure(urls)
            else:
                url_absolute = urljoin(base_url, urls)
                url_absolute = urldefrag(url_absolute)
                urls = await self.correct_url_structure(url_absolute[0])


            urls = unquote(urls)
            
            print()
            print()
            
            # put in the parser_server_queue for server to consume. 
            await parser_server_queue.put(urls)
             
        return "DONE" 
