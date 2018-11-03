"""Scrapy
Multi faceted scraping utility. All the public methods of the Scrapy python module are in this file! For more
information check out the README.md or https://www.github.com/politeauthority/scrapy

Author: @politeauthority
"""

from datetime import datetime
import logging
import os
from random import shuffle
from six import string_types

import requests

from .base_scrapy import BaseScrapy
from .parse_response import ParseResponse
from . import user_agent


class Scrapy(BaseScrapy):

    def __init(self):
        """
        Scrapy constructor. Here we set the default, user changable class vars.

        :class param headers: Any extra headers to add to the response. This can be maniuplated at any time and applied
            just before each request made.
        :class type headers: dict

        :class param user_agent: User setable User Agent to send on every request. This can be updated at any time.
        :class type user_agent: str

        :class param mininum_wait_time: Minimum ammount of time to wait before allowing the next request to go out.
        :class type mininum_wait_time: int

        :class param wait_and_retry_on_connection_error: Time to wait and then retry when a connection error has been
            hit.
        :class type wait_and_retry_on_connection_error: int

        :class param retries_on_connection_failure: Ammount of retry attemps to make when a connection_error has been
            hit.
        :class type retries_on_connection_failure: int

        :class param max_content_length: The maximum content length to download with the Scrapy "save" method, with
            raise as exception if it has surpassed that limit. (@todo This needs to be done still.)
        :class type max_content_length: int

        :class param proxy: Proxy to be used for the connection.
        :class type proxy: dict

        **************************************************
        *  Everything below is still to be implemented!  *

        :class param change_user_interval: Changes identity every x requests. @todo: Implement the changing.

        :class param username: User name to use when needing to authenticate a request. @todo Authentication needs to
            be implemented.

        :class param password: Password to use when needing to authenticate a request. @todo Authentication needs to
            be implemented.

        :class param auth_type: Authentication class to use when needing to authenticate a request. @todo
            Authentication needs to be implemented.
        """
        self.headers = {}
        self.user_agent = ""
        self.mininum_wait_time = 0  # Sets the minumum wait time per domain to make a new request in seconds.
        self.wait_and_retry_on_connection_error = 0
        self.retries_on_connection_failure = 5
        self.max_content_length = 200000000  # Sets the maximum downloard size, default 200 MegaBytes, in bytes.
        self.proxy = {}

        self.change_identity_interval = 10
        self.username = None
        self.password = None
        self.auth_type = None
        super().__init__()

    def request(self, method, url, payload={}):
        """
        Wrapper for the Requests python module's get method, adds in extras such as headers and proxies where
        applicable.

        :param method: The method for the request action to use. "GET", "POST", "PUT", "DELETE"
        :type method: string
        :param url: The url to fetch.
        :type: url: str
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        response = self._make_request(method, url, payload)

        return response

    def get(self, url, payload={}):
        """
        Wrapper for the Requests python module's get method, adds in extras such as headers and proxies where
        applicable.

        :param url: The url to fetch.
        :type: url: str
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        response = self._make_request("GET", url, payload)

        return response

    def post(self, url, payload={}):
        """
        Wrapper for the Requests python module's post method, adds in extras such as headers and proxies where
        applicable.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The data to be sent over POST.
        :type payload: dict
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        response = self._make_request("POST", url, payload)
        return response

    def put(self, url, payload={}):
        """
        Wrapper for the Requests python module's put method, adds in extras such as headers and proxies where
        applicable.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The data to be sent over POST.
        :type payload: dict
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        response = self._make_request("PUT", url, payload)
        return response

    def delete(self, url, payload={}):
        """
        Wrapper for the Requests python module's DELETE method, adds in extras such as headers and proxies where
        applicable.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The data to be sent over POST.
        :type payload: dict
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        response = self._make_request("DELETE", url, payload)
        return response

    def use_random_user_agent(self):
        """
        Sets a random, common browser's User Agent string as our own.

        """
        self.random_user_agent = True
        self.user_agent = user_agent.get_random_ua()

    def get_public_proxies(self, continents=[], ssl_only=False):
        """
        Gets list of free public proxies and loads them into a list, currently just selecting from free-proxy-list.
        @todo: Add filtering by country/ continent.

        :returns: The proxies to be used.
        :rtype: list
        """
        proxies_url = "https://free-proxy-list.net/"
        response = self.get(proxies_url)
        proxies = ParseResponse(response).freeproxylistdotnet(continents)
        if continents or ssl_only:
            if continents and isinstance(continents, string_types):
                continents = [continents]
                print(continents)
            proxies = self._filter_public_proxies(proxies, continents, ssl_only)
        else:
            # Shuffle the proxies so concurrent instances of Scrapy wont use the same proxy
            shuffle(self.proxy_bag)

        return proxies

    def use_random_public_proxy(self, continents=[], ssl_only=False, test_proxy=True):
        """
        Gets proxies from free-proxy-list.net and loads them into the self.proxy_bag. The first element in the
        proxy_bag is the currently used proxy.

        :param continents: Filters proxies to either  just a single continent, or if list is used, orders proxies in
            based off of the order contients are listed within the 'contenient' list.
        :type continents: stror list
        :param ssl_only: Select only proxies fully supporting SSL.
        :type ssl_only: bool
        :param test_proxy: Tests the proxy to see if it's up and working.
        :type test_proxy: bool
        """
        logging.debug("Filling proxy bag")
        self.random_proxy_bag = True
        if continents and isinstance(continents, string_types):
            continents = [continents]

        self.proxy_bag = self.get_public_proxies(continents)

        self.reset_proxy_from_bag()
        self._setup_proxies()
        if not test_proxy:
            return

        logging.info("Testing Proxy: %s (%s)" % (self.proxy_bag[0]["ip"], self.proxy_bag[0]["location"]))
        proxy_test_urls = ["http://www.google.com"]
        for url in proxy_test_urls:
            self.get(url)
        logging.debug("Registered Proxy %s (%s)" % (self.proxy_bag[0]["ip"], self.proxy_bag[0]["location"]))

    def use_skip_ssl_verify(self):
        """
        Sets Scrapy up to not force a valid certificate return from the server. This exists mostly because I was
        running into some issues with self signed certs. This can be enabled/disabled at anytime through execution.

        """
        self.ssl_verify = False

    def stop_skip_ssl(self):
        """
        Sets Scrapy up to go back to throwing an error on SSL validation errors.

        """
        self.ssl_verify = True

    def save(self, url, destination, payload={}):
        """
        Saves a file to a destination on the local drive. Good for quickly grabbing images from a remote site.

        :param url: The url to fetch.
        :type: url: str
        :param destination: Where on the local filestem to store the image.
        :type: destination: str
        :param payload: The data to be sent over GET.
        :type payload: dict
        """
        h = requests.head(url, allow_redirects=True)
        header = h.headers
        content_type = header.get("content-type")
        if "text" in content_type.lower():
            return False
        if "html" in content_type.lower():
            return False

        # Check content length
        content_length = header.get("content-length", None)
        if content_length.isdigit():
            content_length = int(content_length)
            if content_length > self.max_content_length:
                logging.warning("Remote content-length: %s is greater then current max: %s")
                return

        # Get the file
        response = self.get(url, payload=payload)

        # Figure out where to save the file.
        self._prep_destination(destination)
        if os.path.isdir(destination):
            phile_name = url[url.rfind("/") + 1:]
            full_phile_name = os.path.join(destination, phile_name)
        else:
            full_phile_name = destination
        open(full_phile_name, "wb").write(response.content)

        return full_phile_name

    def search(self, query, engine="duckduckgo"):
        """
        Runs a search query on a search engine with the current proxy, and returns a parsed result set.
        Currently only engine supported is duckduckgo.

        :param query: The query to run against the search engine.
        :type query: str
        :param engine: Search engine to use, default "duckduckgo".
        :type engine: str
        :returns: The results from the search engine.
        :rtype: dict
        """
        response = self.get("https://duckduckgo.com/html/?q=%s&ia=web" % query)
        if not response.text:
            return {}

        parsed = self.parse(response)
        results = parsed.duckduckgo_results()
        ret = {
            "response": response,
            "query": query,
            "results": results,
            "parsed": parsed,
        }
        return ret

    def check_tor(self):
        """
        Checks the Tor Projects page "check.torproject.org" to see if we"re running through a tor proxy correctly, and
        exiting through an actual tor exit node.
        @todo: Need to run this successfull to get the tor success page!!

        :returns: Whether or not your proxy is using Tor and Scrapy is connected to it.
        :params: bool
        """
        response = self.get("https://check.torproject.org")
        parsed = self.parse(response)
        title = parsed.get_title()
        if title == "Sorry. You are not using Tor.":
            return False
        elif title == "yeah":
            return True
        return None

    def parse(self, response=None):
        """
        Parses a response from the scraper with the ParseResponse module which leverages Beautiful Soup.

        :param response: Optional content to parse, or will use the last response.
        :type response: Response obj
        :returns: Parsed response, with bs4 parsed soup.
        :type: ParsedResponse obj
        """
        # if not self.last_response and not response:
        #     logging.warning("No response to parse")
        #     return
        if response:
            x = ParseResponse(response)
            return x
        else:
            return ParseResponse(self.last_response)

    def get_outbound_ip(self):
        """
        Gets the currentoutbound IP address for scrappy and sets the self.outbound_ip var.

        :returns: The outbound ip address for the proxy.
        :rtype: str
        """
        ip_websites = ["http://icanhazip.com/"]
        for ip in ip_websites:
            response = self.get(ip)
            if response.status_code != 200:
                logging.warning("Unable to connect to %s for IP.")
                continue

            if response.text != self.outbound_ip:
                self.outbound_ip = response.text.strip()
            return self.outbound_ip

        logging.error("Could not get outbound ip address.")

        return False

    def reset_identity(self):
        """
        Resets the User Agent String if using random user agent string (use_random_user_agent).
        Resets the proxy being used if (use_proxy_bag) and removes the current proxy from bag.

        """
        if self.random_user_agent:
            self.user_agent = user_agent.get_random_ua(except_user_agent=self.user_agent)

        if self.random_proxy_bag:
            self.reset_proxy_from_bag()

    @staticmethod
    def url_concat(*args):
        """
        Concats all args with slashes as needed.
        @note this will probably move to a utility class sometime in the near future.

        :param args: All the url components to join.
        :type args: list
        :returns: Ready to use url.
        :rtype: str
        """
        url = ""
        for url_segment in args:
            if url and url[len(url) - 1] != "/" and url_segment[0] != "/":
                url_segment = "/" + url_segment
            url += url_segment

        return url

    @staticmethod
    def json_date(the_date=None):
        """
        Concats all args with slashes as needed.
        @note this will probably move to a utility class sometime in the near future.

        :param the_date: Datetime to convert, or if None, will use now.
        :type the_date: <DateTime> or None
        :returns: Jsonable date time string
        :rtype: str
        """
        if not the_date:
            the_date = datetime.now()
        ret = the_date.strftime("%Y-%m-%d %H:%M:%S")

        return ret

# End File: scrapy/scrapy/__init__.py
