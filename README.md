<h1> Web-Crawler </h1>


<h2>Disclaimer</h2> : <h4>This Web-Crawler is an integral part of an on-going project and is not meant for use by anyone else. These files are only for reading purpose and                             should not be downloaded or forked or copied in anyway. Any such activity will not be welcomed. Basic purpose of this commit is to store our work online                         and</h4> <h3>NOT TO BE COPIED</h3>.






<h3>The Crawler is divided into 8 scripts:</h3>

1. asyncio_crawler.py
2. crawler.py
3. compressor.py
4. parse.py
5. server.py
6. proxy_server.py
7. dbconnections.py
8. dboperations.py


<h3>The crawler workflow is cyclic :</h3> 

<h4>Crawler -------------> Compressor ---------------> MongoDb --------------> Parse --------------> Server --------------> Crawler</h4>


<h3>Role of each file is described below :</h3>

<h4>asyncio_crawler.py</h4> : This is Central file used to maintain cyclic flow of entire process. Uses Asynchronous programming to improve efficiency of the cyclic stucture.
                        to start the cyclic flow, the crawler is fed up with some uncrawled links stored in MongoDb database. It then starts the cyclic flow and maintains the  
                        cycle.


<h4>crawler.py</h4> : This downloads web-pages and store them in local directory. For now, web-pages with MIME type with schema as text can be downloaded.
                      If a page throws status error other than 200, it is stored separately in the database for feeding these web-pages to asyncio_crawler.py to initiate the     
                      cycle again.For pages of MIME types with schema other than text, are stored separately in a collection named 'Not Text'.


<h4>compressor.py</h4> : Reads file store on the local directory by crawler and push them into MongoDb database in collection https3. Before pushing, pages are compressed using                          in-biult MongoDb functionality.


<h4>parse.py</h4> : Read random files which are not yet parsed from the https3 collection. It then uses BeautifulSoup parser to extract all the 'a' tags and 'href' and pass them                     to server.py.
           

<h4>server.py</h4> : This is written to check if a link to be crawled, is already crawled or not. If crawled, the link is not further crawled and else is crawled. If a link can                      be crawled, it is first entered into database named 'Server' and then passed to crawler.py.
            
            
<h4>dbconnections.py</h4> : Is a centralised file for establishing connection with MongoDb cluster and then with its databases and collections.


<h4>dboperations.py</h4> : Contains all possible MongoDb queries required to complete the task.


<h4>proxy_server.py</h4> : Written to enable proxy rotation to prevent web sites form blocking the crawler. This is not very affective because of free-proxies. tried User-Agents                            rotation as well but could not succesfully use it.
                  
          
<h3>MongDb Structure:</h3> 

Database 1 : Server : 2 Collections ----->  https, http to store URLs of different schemas and to be used by server.py
Database 2 : Compressor : 3 Collections ------> https3, Not Crawled, Not Text to be used by multiple scripts.





*This project is done in collaboration with <h5>Shivam Yadav</h5> (https://github.com/ExpressHermes) and our contributions are mentioned below*:

<h5>Ansh Lehri Contribution (Repository Owner)</h5>: Structure and Workflow Design, Writing asyncio_crawler.py, crawler.py, parse.py, proxy_Server.py parts of 
                                                     dboperations.py(5%) but major contribution is of Shivam Yadav.


<h5>Shivam Yadav Contribution</h5>: Writing scripts - server.py, compressor.py, dbconnection.py, dboperations.py, managing MongoDb database.

<h4>The Crawler is up and running on AWS EC2 instance, managed by Ansh Lehri.</h4>                  
