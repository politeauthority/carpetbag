"""CarpetBag
Multi faceted scraping utility. All the public methods of the CarpetBag python module are in this file! For more
information check out the README.md or https://www.github.com/politeauthority/carpetbag

Author: @politeauthority
Source: https://www.github.com/politeauthority/carpetbag
"""

import logging
import os
from random import shuffle

import requests
import user_agent

from .base_carpetbag import BaseCarpetBag
from .parse_response import ParseResponse
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
            self.user_agent = self.get_new_user_agent()
            return True
        else:
            self.random_user_agent = False
            self.user_agent = ""
            return False

    def get_new_user_agent(self):
        """
        Gets a new user agent string from the user_agent module, making sure that if one has already been selected, it's
        not reused.

        :returns: A brand new user agent string.
        :rtype: str
        """
        new_user_agent = user_agent.generate_navigator()["user_agent"]
        if new_user_agent == self.user_agent:
            self.get_new_user_agent()

        return new_user_agent

    def get_public_proxies(self, continent=""):
        """
        Gets list of free public proxies and loads them into a list, currently just selecting from free-proxy-list.

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
            }
            response = self._make_internal("proxies", payload)
        except errors.NoRemoteServicesConnection:
            logging.error("Unable to connect to Bad-Actor.Services")
            raise errors.NoRemoteServicesConnection

        try:
            self.proxy_bag = response.json()["objects"]
        except Exception:
            logging.error("ERROR: Coud not get proxies. %s" % response.text)
            return False

        logging.debug("Fetched %s proxies" % len(self.proxy_bag))

        # Shuffle the proxies so concurrent instances of CarpetBag wont use the same proxy
        shuffle(self.proxy_bag)

        return self.proxy_bag

    def use_random_public_proxy(self, val=True, test_proxy=False):
        """
        Gets proxies from free-proxy-list.net and loads them into the self.proxy_bag. The first element in the
        proxy_bag is the currently used proxy.

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
            self.logger.debug("Proxy Bag already built, not getting more.")
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
        if len(self.proxy_bag) == 0:
            self.logger.debug("Changing proxy")
            self.logger.error("Proxy bag is empty! Cannot reset Proxy from Proxy Bag.")
            raise errors.EmptyProxyBag

        # Remove the current proxy from the proxy bag if one is set.
        if self.proxy:
            self.logger.debug("Changing proxy")
            del self.proxy_bag[0]
        else:
            self.logger.debug("Selecting proxy")

        if len(self.proxy_bag) == 0:
            self.logger.debug("Changing proxy")
            self.logger.error("Proxy bag is empty! Cannot reset Proxy from Proxy Bag.")
            raise errors.EmptyProxyBag


        self.proxy_current = self.proxy_bag[0]
        if "http" in self.proxy:
            self.proxy.pop("http")
        if "https" in self.proxy:
            self.proxy.pop("https")

        self.logger.debug("New Proxy: %s (%s - %s)" % (
            self.proxy_current["address"],
            self.proxy_current["continent"],
            self.proxy_current["country"]))

        if self.proxy_current["ssl"]:
            self.proxy = {"https": self.proxy_current["address"]}
        else:
            self.proxy = {"http": self.proxy_current["address"]}

    def use_skip_ssl_verify(self, val=True, force=False):
        """
        Sets CarpetBag up to not force a valid certificate return from the server. This exists mostly because I was
        running into some issues with self signed certs. This can be enabled/disabled at anytime through execution.

        ** WARNING ** Would not typically recommend using "force=True", unless retrying a request is extermly taxing
        and you're willing to accept the risk of using a non verified data source!

        :param val: Whether or not to enable or disable skipping SSL Cert validation.
        :type val: bool
        :param force: Will force CarpetBag to completely skip all verification of SSL Certs, becareful using this.
        :type force: bool
        :returns: The value CarpetBag is configured to use for self.ssl_verify
        :rtype: bool
        """
        if val:
            self.ssl_verify = False
        else:
            self.ssl_verify = True

        if force:
            self.force_skip_ssl_verify = True
        else:
            self.force_skip_ssl_verify = False

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
        head_args["verify"] = False
        h = requests.head(**head_args)
        header = h.headers
        content_type = header.get("content-type")

        # Figure out the local file name and check if it's available.
        local_phile_name = self._determine_save_file_name(url, content_type, destination)
        if os.path.exists(local_phile_name) and not overwrite:
            logging.error("File %s already exists, use carpetbag.save(overwrite=True) to overwrite." % local_phile_name)
            raise errors.CannotOverwriteFile

        # Check content length
        content_length = header.get("content-length", None)
        if content_length.isdigit():
            content_length = int(content_length)
            if content_length > self.max_content_length:
                logging.warning("Remote content-length: %s is greater then current max: %s")
                return False

        # Get the file.
        response = self.get(url, payload=payload)

        open(local_phile_name, "wb").write(response.content)

        return local_phile_name

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
            logging.warning("Tor is NOT properly configured.")
            return False
        elif title == "Congratulations. This browser is configured to use Tor.":
            logging.info("Tor is properly configured.")
            return True

        logging.error("There was an unexpected error checking if Tor is properly configured.")
        return False

    def parse(self, response=None):
        """
        Parses a response from the scraper with the ParseResponse module which leverages Beautiful Soup.

        :param response: Optional content to parse, or will use the last response.
        :type response: <Response> obj
        :returns: Parsed response, with bs4 parsed soup.
        :type: <ParseResponse> obj
        """
        if response:
            return ParseResponse(response)
        else:
            return ParseResponse(self.last_response)

    def get_outbound_ip(self):
        """
        Gets the currentoutbound IP address for scrappy and sets the self.outbound_ip var.

        :returns: The outbound ip address for the proxy.
        :rtype: str
        """
        try:
            response = self._make_internal("ip")
        except errors.NoRemoteServicesConnection:
            logging.error("Unable to connect to Bad-Actor.Services")
            return False

        self.outbound_ip = response.json()["ip"]

        return self.outbound_ip

    def reset_identity(self):
        """
        Resets the User Agent String if using random user agent string (use_random_user_agent).
        Resets the proxy being used if (use_proxy_bag) and removes the current proxy from bag.

        """
        if self.random_user_agent:
            self.user_agent = self.get_new_user_agent()

        if self.random_proxy_bag:
            self.reset_proxy_from_bag()

        return True

    def test_public_proxy(self, retry_on_failure=True):
        """
        Tests the current public proxy to see if it is working. If it's not and the user is using proxy bag, we'll
        find a new one.
        @todo: Needs unit test.

        :param retry_on_failure: Whether or not to get a new proxy and retry if a proxy fails.
        :type retry_on_failure: bool
        :returns: Success or failure of a proxy.
        :rtype: bool
        """
        logging.info("Testing Proxy: %s (%s)" % (self.proxy_bag[0]["ip"], self.proxy_bag[0]["country"]))
        self.use_skip_ssl_verify()
        self.headers = {"Content-Type": "application/json"}
        test_url = self.remote_service_api.replace("api", "test")

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

    def set_header(self, key, value):
        """
        Sets the headers to be sent over requests.

        :param key: The header key.
        :type key: str
        :param value: The header value to be set.
        :type value: dict
        :returns: The headers to be sent to the request.
        :rtype: dict
        """
        self.headers[key] = value

        return self.headers

    def set_header_once(self, key, value):
        """
        Sets a header once for a request that returns successfully.

        :param key: The header key.
        :type key: str
        :param value: The header value to be set.
        :type value: dict
        :returns: The headers to be sent to the request.
        :rtype: dict
        """
        self.one_time_headers.append(key)
        self.set_header(key, value)

        return self.headers

    def send_usage_stats(self, api_key, non_proxy_user_ip, val=True):
        """
        Sends usage stats to bad-actor.services, this helps rate the quality of proxy services so only the best proxies
        are selected.

        :param api_key: The bad-actor.services API key for submitting usage data.
        :type api_key: str
        :param non_proxy_user_ip: The IP address of the user with out a proxy, to help determine proxy quality.
        :type non_proxy_user_ip: str
        :param val: Whether or not to start or stop sending usage data.
        :type val: bool
        :returns: Current value of usage stat sending.
        :rtype: bool
        """
        self.send_usage_stats_val = val
        self.usage_stats_api_key = api_key
        self.non_proxy_user_ip = non_proxy_user_ip
        return val


# End File: carpetbag/carpetbag/__init__.py
