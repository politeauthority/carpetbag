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
    print('Setup the bagger.')
    bagger = CarpetBag()

    print('Configure the bagger to use a random user agent.')
    bagger.use_random_user_agent()

    print('Configure the bagger to use a random public proxy.')
    bagger.use_random_public_proxy()
    import pdb; pdb.set_trace()

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


if __name__ == '__main__':
    public_proxy_with_reset()

# EndFile: carpetbag/example.py
