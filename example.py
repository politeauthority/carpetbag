import logging

from scrapy import Scrapy

log = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
log.addHandler(console)

scraper = Scrapy()

scraper.use_random_user_agent()
scraper.use_random_public_proxy()
try:
    x = scraper.get('http://www.google.com')
except requests.requests.exceptions.ConnectionError:
    print('resetting bag')
    scraper.reset_proxy_from_bag()
    x = scraper.get('http://www.google.com')

print(x)

# EndFile: scrapy/example.py
