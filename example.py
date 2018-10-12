"""Examples

"""

import requests
import logging

from scrapy import Scrapy

log = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
log.addHandler(console)


def public_proxy_with_reset():
    """
    Example grabbing a site with a free public proxy, and reset the proxy if we get a connection error.

    """
    scraper = Scrapy()
    scraper.use_random_user_agent()
    scraper.use_random_public_proxy()
    try:
        response = scraper.get('http://www.google.com')
    except requests.requests.exceptions.ConnectionError:
        print('resetting bag')
        scraper.reset_proxy_from_bag()
        response = scraper.get('http://www.google.com')
    print(response)

# EndFile: scrapy/example.py
