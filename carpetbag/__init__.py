"""CarpetBag
Multi faceted scraping utility. All the public methods of the CarpetBag python module are in this file! For more
information check out the README.md or https://www.github.com/politeauthority/carpetbag

Author: @politeauthority
"""

import logging
import os
from random import shuffle

import requests

from .base_carpetbag import BaseCarpetBag
from .parse_response import ParseResponse
from . import carpet_tools as ct
from . import user_agent
from . import errors


class CarpetBag(BaseCarpetBag):

    def __init__(self):
        """
        CarpetBag constructor. Here we set the default, user changable class vars.

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

        :class param max_content_length: The maximum content length to download with the CarpetBag "save" method, with
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
        self.__version__ = "0.0.1"
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

    def use_random_user_agent(self, val=True):
        """
        Sets a random, common browser's User Agent string as our own.

        :param val: Whether or not to enable random user agents.
        :type val: bool
        :returns: Whether or not random public proxying is happening.
        :rtype: bool
        """
        if val:
            self.random_user_agent = True
            self.user_agent = user_agent.get_random_ua()
            return True
        else:
            self.random_user_agent = False
            self.user_agent = ""
            return False

    def get_public_proxies(self, continent="", ssl_only=False):
        """
        Gets list of free public proxies and loads them into a list, currently just selecting from free-proxy-list.
        @todo: Add filtering by country/ continent.


        :param continent: Filters proxies to either  just a single continent, or if list is used, orders proxies in
            based off of the order contients are listed within the "contenient" list.
        :type continent: str or list
        :param ssl_only: Select only proxies fully supporting SSL.
        :type ssl_only: bool
        :returns: The proxies to be used.
        :rtype: list
        """
        logging.debug("Filling proxy bag")

        try:
            payload = {
                "continent": continent,
                "ssl_only": ssl_only
            }
            response = self._make_internal('proxies', payload)
        except errors.NoRemoteServicesConnection:
            logging.error("Unable to connect to Bad-Actor.Services")
            raise errors.NoRemoteServicesConnection

        self.proxy_bag = response["objects"]

        # Shuffle the proxies so concurrent instances of CarpetBag wont use the same proxy
        shuffle(self.proxy_bag)

        return self.proxy_bag

    def use_random_public_proxy(self, val=True, test_proxy=False):
        """
        Gets proxies from free-proxy-list.net and loads them into the self.proxy_bag. The first element in the
        proxy_bag is the currently used proxy.
        @todo: NEEDS UNIT TEST!


        :param val: Whether or not to enable random public proxies.
        :type val: bool
        :param test_proxy: Tests the proxy to see if it's up and working.
        :type test_proxy: bool
        :returns: Whether or not random public proxying is happening.
        :rtype: bool
        """
        if not val:
            self.random_proxy_bag = False
            return False
        self.random_proxy_bag = True

        if not self.proxy_bag:
            self.proxy_bag = self.get_public_proxies()

        self.reset_proxy_from_bag()
        if not test_proxy:
            return True

        if self.test_public_proxy():
            return True

        return False

    def reset_proxy_from_bag(self):
        """
        Grabs the next proxy inline from the self.proxy_bag, and removes the currently used proxy. If proxy bag is
        empty, raises the EmptyProxyBag error.

        :raises: carpetbag.erros.EmptyProxyBag
        """
        self.logger.debug("Changing proxy")
        if len(self.proxy_bag) == 0:
            self.logger.error("Proxy bag is empty! Cannot reset Proxy from Proxy Bag.")
            raise errors.EmptyProxyBag

        # Remove the current proxy if one is set.
        if self.proxy:
            del self.proxy_bag[0]

        chosen_proxy = self.proxy_bag[0]
        self.proxy = {"http": chosen_proxy["address"]}

        if chosen_proxy["ssl"]:
            self.proxy = {"https": chosen_proxy["address"]}

    def use_skip_ssl_verify(self, val=True):
        """
        Sets CarpetBag up to not force a valid certificate return from the server. This exists mostly because I was
        running into some issues with self signed certs. This can be enabled/disabled at anytime through execution.

        :param val: Whether or not to enable or disable skipping SSL Cert validation.
        :type val: bool
        :returns: The value CarpetBag is configured to use for self.ssl_verify
        :rtype: bool
        """
        if val:
            self.ssl_verify = False
        else:
            self.ssl_verify = True

        return val

    def save(self, url, destination, payload={}, overwrite=False):
        """
        Saves a file to a destination on the local drive. Good for quickly grabbing images from a remote site.

        :param url: The url to fetch.
        :type: url: str
        :param destination: Where on the local filestem to store the image.
        :type: destination: str
        :param payload: The data to be sent over GET.
        :type payload: dict
        :param overwrite: Overwrite if file already exists in the destination.
        :type overwrite: bool
        :returns: The file path of the file written.
        :rtype: str
        """
        head_args = self._fmt_request_args("GET", self.headers, url, payload)
        head_args.pop("method")
        head_args['verify'] = False
        h = requests.head(allow_redirects=True, **head_args)
        header = h.headers
        content_type = header.get("content-type")

        # Check content length
        content_length = header.get("content-length", None)
        if content_length.isdigit():
            content_length = int(content_length)
            if content_length > self.max_content_length:
                logging.warning("Remote content-length: %s is greater then current max: %s")
                return False

        # Get the file.
        response = self.get(url, payload=payload)

        # Figure out where to save the file.
        if os.path.isdir(destination):
            destination_dir = destination

        elif destination[len(destination) - 1] == '/':
            destination_dir = destination
        else:
            destination_dir = destination[:destination.rfind('/')]

        destination_last = destination[destination.rfind("/") + 1:]
        self._prep_destination(destination_dir)

        # Decide the file name.
        file_extension = self._content_type_to_extension(content_type)
        url_disect = ct.url_disect(url)

        # If the chosen destination is a directory, find a name for the file.
        if os.path.isdir(destination):
            phile_name = url_disect["last"]
            if '.' not in phile_name:
                if file_extension:
                    phile_name = phile_name + file_extension

            elif "." in url_disect["last"]:
                file_extension = url_disect["url"][:url_disect["url"].rfind(".") + 1]
                phile_name = url_disect["last"]
                full_phile_name = os.path.join(destination, phile_name)

        else:

            # If the choosen drop is not a directory, use the name given.
            if "." in destination_last:
                full_phile_name = os.path.join(destination_dir, destination_last)

            elif "." in url_disect["last"]:
                phile_name = url_disect["last"][:url_disect["last"].rfind(".")]
                file_extension = url_disect["last"][url_disect["last"].rfind(".") + 1:]

                full_phile_name = destination_dir + "%s.%s" % (phile_name, file_extension)

        if os.path.exists(full_phile_name) and not overwrite:
            logging.error("File %s already exists, use carpetbag.save(overwrite=True) to overwrite." % full_phile_name)
            raise errors.CannotOverwriteFile

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

        :returns: Whether or not your proxy is using Tor and CarpetBag is connected to it.
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
        try:
            response = self._make_internal('ip')
        except errors.NoRemoteServicesConnection:
            logging.error("Unable to connect to Bad-Actor.Services")
            return False

        self.outbound_ip = response["ip"]

        return self.outbound_ip

    def reset_identity(self):
        """
        Resets the User Agent String if using random user agent string (use_random_user_agent).
        Resets the proxy being used if (use_proxy_bag) and removes the current proxy from bag.

        """
        if self.random_user_agent:
            self.user_agent = user_agent.get_random_ua(except_user_agent=self.user_agent)

        if self.random_proxy_bag:
            self.reset_proxy_from_bag()

        return True

    def test_public_proxy(self, retry_on_failure=True):
        """
        Tests the current public proxy to see if it is working. If it's not and the user is using proxy bag, we'll
        find a new one.

        """
        logging.info("Testing Proxy: %s (%s)" % (self.proxy_bag[0]["ip"], self.proxy_bag[0]["country"]))
        self.use_skip_ssl_verify()
        self.headers = {"Content-Type": "application/json"}
        test_url = self.remote_service_api.replace('api', 'test')

        test_response = self.get(test_url)
        self.use_skip_ssl_verify(False)

        # if not test_response:
        #     logging.error("Could not find a working proxy.")
        #     return False

        logging.debug("Registered Proxy %s (%s) Test Request Took: %s" % (
            self.proxy_bag[0]["ip"],
            self.proxy_bag[0]["country"],
            test_response.roundtrip))

        return True

# End File: carpetbag/carpetbag/__init__.py
