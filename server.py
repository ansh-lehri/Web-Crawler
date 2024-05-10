# includes methods to check if the url to be crawled has already been crawled
# or not. If already crawled, it is not forwarded else pushed into server_crawler
# linkage for cralwer to download and save.

# importing from user-developed module.
from dboperations import MongoDB


class Server:

    def __init__(self):
        pass




    async def handle_urls(self, url, mongodb):
        
        # calls clean_url method and check_and_insert to check if url should be 
        # crawled and return YES if it should else NO

        cleaned_url, url_type = await self.clean_url(url)
        answer = await self.check_and_insert(cleaned_url, url_type, mongodb)
        return answer




    async def clean_url(self, url):

        """ remove https:// and www. from start of url """
        url_type = "https"

        cleaned_url = url
        if url[:8] == "https://":
            cleaned_url = url[8:]
            url_type = "https"

        elif url[:8] == "http://":
            cleaned_url = url[8:]
            url_type = "http"

        if cleaned_url[:4] == "www.":
            cleaned_url = cleaned_url[4:]

        if cleaned_url[-1] == "/":
            cleaned_url = cleaned_url[:-1]

        return (cleaned_url, url_type)




    async def check_and_insert(self, url, url_type, mongodb):

        """Checks if the url exists in DB. If url does not exist,
        creates a new doc with given url as _id
        """
        doc = mongodb.fetch_doc(url, coll=url_type)
        if doc:
            return "NO"
        else:
            try:
                data = {"_id": url}
                if mongodb.create_doc(data=data, coll=url_type):
                    return "YES"
            except Exception as e:
                return "NO"

 
