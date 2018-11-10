"""Examples

@todo: More/better examples!
"""

import requests
import logging

from carpetbag import CarpetBag

log = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
log.addHandler(console)


def public_proxy_with_reset():
    """
    Example grabbing a site with a random user agent and free public proxy.
    Then we reset the proxy if we get a ConnectionError.

    """
    bagger = CarpetBag()
    bagger.use_random_user_agent()
    bagger.use_random_public_proxy()
    try:
        response = bagger.get('http://www.google.com')
    except requests.requests.exceptions.ConnectionError:
        print('resetting bag')
        bagger.reset_proxy_from_bag()
        response = bagger.get('http://www.google.com')
    print(response)


def public_proxy_continent():
    """
    """
    bagger = CarpetBag()
    bagger.use_random_public_proxy(continents=['North America'], ssl_only=True)


# EndFile: carpetbag/example.py
