# Creates proxy pool using fake_proxy package, to use in proxy rotation.

# importing from builtin python packages and installed libraries.
import fake_proxy
import random


class Proxy:

    def __init__(self):

        self.proxy_number = random.randint(10,20)
        self.proxy_pool = self.fake_proxy()
        
    
    def fake_proxy(self):

        proxy = fake_proxy.get(amount=self.proxy_number,proxy_type='https')
        proxies=[]
        for i in proxy:
            proxies.append("https://"+i['ip']+":"+i['port'])
        return proxies

