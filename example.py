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
    print("Setup the bagger.")
    bagger = CarpetBag()

    print("Configure the bagger to use a random user agent.")
    bagger.use_random_user_agent()

    print("Configure the bagger to use a random public proxy.")
    bagger.use_random_public_proxy()

    try:
        response = bagger.get("http://www.google.com")
    except requests.requests.exceptions.ConnectionError:
        print("resetting bag")
        bagger.reset_proxy_from_bag()
        response = bagger.get("http://www.google.com")
    print(response)


def demo_tor_usage():
    bagger = CarpetBag()
    bagger.proxy["https"] = "https://tor:8118"
    tor = bagger.check_tor()
    if tor:
        print("Congratulations, Tor is working properly")
    else:
        print("Sorry, something is not working connecting to Tor.")

    ip = bagger.get_outbound_ip()
    print(ip)


demo_tor_usage()


# EndFile: carpetbag/example.py
