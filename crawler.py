# inludes methods to extract the web-page of corresponding url,
# writing them in a file with proper extension and store in a local directory.
# for now only 'text' type files are being downloaded and saved. 
#  urls of all other types are saved separately.

# importing built-in libraries and installed python packages
import os.path
import queue
import re
import requests
import sys
import threading
import time
from itertools import cycle
from bs4 import BeautifulSoup,SoupStrainer
from pprint import pprint

# importing from user-developed module
from dboperations import MongoDB



class Scraper:

    def __init__(self):

        self.path = "/tmp"



    async def write_file(self, file, request, url):
        
        flag = 1

        for chunk in request.iter_content(chunk_size=1024):
            if chunk:
                # used "iso-8859-1" as no other was working completely.
                soup = BeautifulSoup(chunk, "html.parser", from_encoding="iso-8859-1")
            
                # flag is used as signal to create a new tag called "singularity" 
                # with attribute 'href = {url of the page being saved}' inside each 
                # file. Done to access url of page while parsing and in compressor.
                 
                if flag:
                    tag = soup.html
                    if tag==None:
                        print("R    E     T     U      R      N       I       N      G")
                        file.close()
                        return
                    new_tag = soup.new_tag("singularity", href=url)
                    if new_tag==None:
                        print("N  E  W   T  A  G  E  R  R  O  R  ==============================  ",url,"  ===================================================    ")
                        file.close()
                        return 
                    tag.append(new_tag)
                    
                    # tag created and flag=0
                    flag = 0

                doc = soup.prettify()
                try:
                    file.write(doc)
                except Exception as e:
                    print(doc_id)
        file.close()
        return 




    async def open_file(self, request, crawler_doc_id, ext, url):
        
        # opens a file with proper extension in the local directory.
        file = open(
            os.path.join(self.path, "Singularity" + f"{crawler_doc_id}" +"."+ ext),
            "w+",
            encoding="utf-8",
        )

        # write_file method is called to write files.
        await self.write_file(file, request, url)
        return 




    def request_access(self, url, proxy):
    
            try:
                r = requests.get(url,stream=True)
            except Exception as e:
                print(e)
                return ""
            else:
                return r




    async def check_extension(self, content_type):
        
        # checks schema of mime-type. If valid, continue and return extension
        # of file else return "Return the Task."

        if re.match(r"^[TEXTtext]", content_type) == None:
            #print("PUSH INTO DATABASE        ------------------------------------------------------------------------------------>", content_type,"                         =======================================")
            return "Return the Task."

        else:
            extension = re.search(r"\/[a-zA-Z]+", content_type)
            ext = extension.group(0)[1:]
            return ext




    async def save_url_page(self, request, url):
        
        # extract mime-type of the url.
        content_type = request.headers.get("content-type")

        # if schema of mime-type is not 'text'; 'Return the Task.' is returned
        # by check_extension method.
        ext = await self.check_extension(content_type)

        if ext=="Return the Task.":
            return "Not successful",""

        return ext,content_type
 
 


    async def server_crawler_buffer(self, url, proxy, to_delete):

        print("TRUE")

        # 'request_access' method to access permission for using the web page
        # proxy is passed to help in proxy rotation

        # returned values are in sequence as following:
        # result, request, ext, content_type, page_status
        # resut ====> successful if url request executed else unsuccessful
        # request ====> request object of url request
        # ext ====> type of web page, html/htm/xml etc.
        # content_type ====> mime type of web page
        # page_status =====> 1. 200 = page exists.
        #                    2. 404 = either page not exists or request blocked by website.
        #                    3. 100 = schema of mime type != text


        request = self.request_access(url, proxy)

        # if url passed is invalid 
        if request=="":
            print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")
            return "unsuccessful","","","",""
        print(request.status_code)

        
        # according to 'request.status_code' and status; tuples are returned 
        # to calling method web_page_downloader in module asyncio_crawler 
        
        if request.status_code == 200:
            
            # if page exists, request and url are passed to save it on disk.
            status,content_type = await self.save_url_page(request, url)
            
            if status=="Not successful":
                return "unsuccessful","","",content_type,"100"
            else:
                return "successful",request,status,content_type,"200"
        else:
            return "unsuccessful","","","","404"











