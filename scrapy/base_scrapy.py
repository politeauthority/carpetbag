"""BaseScrapy

"""
from datetime import datetime
import logging
import math
import os
import time
from random import shuffle
import re

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import tld

from .parse_response import ParseResponse


class BaseScrapy(object):

    def __init__(self):
        """
        Scrapy constructor. Here we set the default, user changable class vars.

        :class param headers: Any extra headers to add to the response. This can be maniuplated at any time and applied
            just before each request made.
        :class type headers: dict

        :class param user_agent: User setable User Agent to send on every request. This can be updated at any time.
        :class type user_agent: str

        :class param random_user_agent: Setting to decide whether or not to use a random user agent string.
        :class type random_user_agent: bool

        :class param skip_ssl_verify: Skips the SSL cert verification. Sometimes this is needed when hitting certs
            given out by LetsEncrypt.
        :class type skip_ssl_verify: bool

        :class param mininum_wait_time: Minimum ammount of time to wait before allowing the next request to go out.
        :class type mininum_wait_time: int

        :class param wait_and_retry_on_connection_error: Time to wait and then retry when a connection error has been
            hit.
        :class type wait_and_retry_on_connection_error: int

        :class param retries_on_connection_failure: Ammount of retry attemps to make when a connection_error has been
            hit.
        :class type retries_on_connection_failure: int

        :class param max_content_length: The maximum content length to download with the Scrapy 'save' method, with
            raise as exception if it has surpassed that limit. (@todo This needs to be done still.)
        :class type max_content_length: int

        :class param proxies: Set of proxies to be used for the connection.
        :class type proxies: dict

        Everything below is still to be implemented!
        :class param change_user_interval: Changes identity every x requests. @todo: Implement the changing.

        :class param username: User name to use when needing to authenticate a request. @todo Authentication needs to
            be implemented.

        :class param password: Password to use when needing to authenticate a request. @todo Authentication needs to
            be implemented.

        :class param auth_type: Authentication class to use when needing to authenticate a request. @todo
            Authentication needs to be implemented.
        """
        logging.getLogger(__name__)
        self.headers = {}
        self.user_agent = ''
        self.random_user_agent = False
        self.skip_ssl_verify = True
        self.mininum_wait_time = 0  # Sets the minumum wait time per domain to make a new request in seconds.
        self.wait_and_retry_on_connection_error = 0
        self.retries_on_connection_failure = 5
        self.max_content_length = 200000000  # Sets the maximum downloard size, default 200 MegaBytes, in bytes.
        self.proxies = {}
        self.username = None
        self.password = None
        self.auth_type = None
        self.change_identity_interval = 0

        # These are private reserved class vars, don't use these!
        self.outbound_ip = None
        self.request_attempts = {}
        self.request_count = 0
        self.request_total = 0
        self.last_request_time = None
        self.last_response = None
        self.manifest = {}
        self.proxy_bag = []
        self.random_proxy_bag = False
        self.send_user_agent = ''
        self._setup_proxies()

    def __repr__(self):
        proxy = ''
        if self.proxies.get('http'):
            proxy = " Proxy:%s" % self.proxies.get('http')
        return '<Scrapy%s>' % proxy

    def _make_request(self, method, url, payload={}, ssl_verify=True):
        """
        Makes the response, over GET, POST or PUT.

        :param method: The method for the request action to use. "GET", "POST", "PUT", "DELETE"
        :type method: string
        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The payload to be sent, if we're making a post request.
        :type payload: dict
        :param ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified the request
            will fail.
        :type ssl_verify: bool
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        if self.skip_ssl_verify:
            ssl_verify = False
        ts_start = int(round(time.time() * 1000))
        url = ParseResponse.add_missing_protocol(url)
        headers = self._get_headers()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self._increment_counters()
        self._handle_sleep(url)

        response = self._make(method, url, headers, payload, ssl_verify)

        if response.status_code >= 500:
            logging.warning('Recieved a server error response %s' % response.status_code)

        roundtrip = self._after_request(ts_start, url, response)
        logging.debug('Repsonse took %s for %s' % (roundtrip, url))

        return response

    def _handle_sleep(self, url):
        """
        Sets scrapy to sleep if we are making a request to the same server in less time then the value of
        self.mininum_wait_time allows for.

        :param url: The url being requested.
        :type url: str
        """
        if not self.mininum_wait_time:
            return

        if not self.last_request_time:
            return

        # Checks that the next server we're making a request to is the same as the previous request.
        # tld.get_fld(self.last_response.url)
        if self._get_domain(self.last_response.url) != self._get_domain(url):
            return

        # Checks the time of the last request and sets the sleep timer for the difference.
        diff_time = datetime.now() - self.last_request_time
        if diff_time.seconds < self.mininum_wait_time:
            sleep_time = self.mininum_wait_time - diff_time.seconds
            logging.debug('Sleeping %s seconds before next request.')
            time.sleep(sleep_time)

    def _get_domain(self, url):
        """
        Tries to get the domain/ip and port from the url we are requesting to.
        @tod: There looks to be an issue with getting an ip address from the url.

        :param url:
        :type urls: str
        :returns: The domain/ip of the server being requested to.
        :rtype: str
        """
        regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        matches = re.finditer(regex, url)
        for matchNum, match in enumerate(matches):
            try:
                return match.group()
            except AttributeError:
                pass

        if '//localhost' in url:
            return 'localhost'

        try:
            return tld.get_fld(url)
        except tld.exceptions.TldDomainNotFound:
            logging.warning('Could not determin domain for %s' % url)
            return ''

    def _get_headers(self):
        """
        Gets headers for the request, checks for user values in self.headers and then creates the rest.

        :returns: The headers to be sent in the request.
        :rtype: dict
        """
        send_headers = {}
        self._set_user_agent()
        if self.send_user_agent:
            send_headers['User-Agent'] = self.send_user_agent

        for key, value in self.headers.items():
            send_headers[key] = value

        return send_headers

    def _setup_proxies(self):
        """
        If an HTTPS proxy is not specified but an HTTP is, use the same for both by default.

        """
        if not self.proxies:
            return
        if 'http' in self.proxies and 'https' not in self.proxies:
            self.proxies['https'] = self.proxies['http']

    def _set_user_agent(self):
        """
        Sets a user agent to the class var if it is being used, otherwise if it's the 1st or 10th request, fetches a new
        random user agent string.

        :returns: The user agent string to be used in the request.
        :rtype: str
        """
        if self.user_agent:
            self.send_user_agent = self.user_agent
            return

    def _make(self, method, url, headers, payload, ssl_verify, retry=0):
        """
        Makes the request and handles different errors that may come about.

        self.wait_and_retry_on_connection_error can be set to add a wait and retry in seconds.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param headers: The headers to be sent on the request.
        :type: headers: dict
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :param ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified the request
            will fail.
        :type ssl_verify: bool
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        logging.debug('Making request: %s' % url)
        request_args = {
            'method': method,
            'url': url,
            'headers': headers,
            'proxies': self.proxies,
            'verify': ssl_verify
        }
        if method == 'GET':
            request_args['params'] = payload
        elif method in ['PUT', 'POST']:
            request_args['data'] = payload

        try:
            response = requests.request(**request_args)

        # Catch Connection Refused Error. This is probably happening because of a bad proxy.
        # Catch an error with the connection to the Proxy
        except requests.exceptions.ProxyError:
            if self.random_proxy_bag:
                logging.warning('Hit a proxy error, picking a new one from proxy bag and continuing.')
                self.reset_proxy_from_bag()
            else:
                logging.warning('Hit a proxy error, sleeping for %s and continuing.' % 5)
                time.sleep(5)

            return self._make(method, url, headers, payload, ssl_verify, retry)

        # Catch an SSLError, seems to crop up with LetsEncypt certs.
        except requests.exceptions.SSLError:
            logging.warning('Recieved an SSLError from %s' % url)
            if self.skip_ssl_verify:
                logging.warning('Re-running request without SSL cert verification.')
                return self._make(method, url, headers, payload, True, retry)
            return self._handle_ssl_error(method, url, headers, payload, retry)

        # Catch the server unavailble exception, and potentially retry if needed.
        except requests.exceptions.ConnectionError:
            if retry == 0 and self.random_proxy_bag:
                self.reset_proxy_from_bag()

            response = self._handle_connection_error(method, url, headers, payload, ssl_verify, retry)
            if response:
                return response

            raise requests.exceptions.ConnectionError

        return response

    def _handle_connection_error(self, method, url, headers, payload, ssl_verify, retry):
        """
        Handles a connection error. If self.wait_and_retry_on_connection_error has a value other than 0 we will wait
        that long until attempting to retry the url again.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param headers: The headers to be sent on the request.
        :type: headers: dict
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :param ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified the request
            will fail.
        :type ssl_verify: bool
        :param retry: Number of attempts that have already been performed for this request.
        :type ssl_verify: int
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj or None
        """
        logging.error('Unabled to connect to: %s' % url)

        total_retries = self.retries_on_connection_failure
        retry += 1
        if retry > total_retries:
            return None

        # if self.proxies and self.proxy_bag:
        #     self._reset_proxy_from_bag()

        if self.retries_on_connection_failure:
            logging.warning(
                'Attempt %s of %s. Sleeping and retrying url in %s seconds.' % (
                    str(retry),
                    total_retries,
                    self.wait_and_retry_on_connection_error))
            if self.wait_and_retry_on_connection_error:
                time.sleep(self.wait_and_retry_on_connection_error)
            return self._make(method, url, headers, payload, ssl_verify, retry)

        return None

    def reset_proxy_from_bag(self):
        """
        Changes the proxy, assuming the current one is no good, it removes it from the proxy bag and loads up the next
        one.

        """
        if not self.proxy_bag:
            return
        logging.debug('Changing proxy')
        self.proxy_bag.pop(0)
        self.proxies['http'] = self.proxy_bag[0]['ip']

    def _handle_ssl_error(self, method, url, headers, payload, ssl_verify, retry):
        """
        Used to catch an SSL issue and allow scrapy to choose whether or not to try without SSL.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param headers: The headers to be sent on the request.
        :type: headers: dict
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :param ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified the request
            will fail.
        :type ssl_verify: bool
        :param retry: Number of attempts that have already been performed for this request.
        :type ssl_verify: int
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj or None
        """
        logging.warning("""There was an error with the SSL cert, this happens a lot with LetsEncrypt certificates. Set the class
            var, self.skip_ssl_verify or use the skip_ssl_verify in the .get(url=url, skip_ssl_verify=True)""")
        if self.skip_ssl_verify:
            logging.warning('Re-running request without SSL cert verification.')
            return self._make(method, url, headers, payload, ssl_verify, retry)
        return False

    def _after_request(self, ts_start, url, response):
        """
        Runs after request opperations, sets counters and run times. This Should be called before any raised known
        execption.

        :param ts_start: The start of the request.
        :type st_start: int
        :param url: The url being requested.
        :type url: str
        :param response: The <Response> object from <Requests>
        :type response: <Response> object
        :returns: The round trip time from the request in milliseconds.
        :type: float
        """
        self.last_response = response
        ts_end = int(round(time.time() * 1000))
        roundtrip = ts_end - ts_start
        self.last_request_time = datetime.now()
        if response:
            response.roundtrip = roundtrip
            response.domain = self._get_domain(url)
        self.ts_start = None
        return roundtrip

    def _increment_counters(self):
        """
        Add one to each request counter after a request has been made.

        """
        self.request_count += 1
        self.request_total += 1

    def _get_proxies(self):
        """
        Gets list of free public proxies and loads them into a list.

        :returns: The proxies to be used.
        :rtype: list
        """
        proxies_url = "https://free-proxy-list.net/"
        response = self.get(proxies_url)
        proxies = ParseResponse(response).freeproxylistdotnet()

        # Shuffle the proxies so multiple instances of Scrapy wont use the same one
        shuffle(proxies)
        return proxies

    def _prep_destination(self, destination):
        """
        Attempts to create the destintion directory path if needed.
        @todo: create unit tests.

        :param destination:
        :type destination:
        :returns: Success or failure of pepping destination.
        :rtype: bool
        """
        if os.path.exists(os.path.isdir(destination)):
            return True
        elif os.path.exists(destination):
            try:
                os.makedirs(destination)
                return True
            except Exception:
                logging.error('Could not create directory: %s' % destination)
                return False

    def _convert_size(self, size_bytes):
        """
        Converts bytes to human readable size.

        :param size_bytes: Size in bytes to measure.
        :type size_bytes: int
        :returns: The size of the var in a human readable format.
        :rtype: str
        """
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

# EndFile: scrapy/base_scrapy.py
