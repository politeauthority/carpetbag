"""Scrapy

"""
from datetime import datetime
import logging
import math
import os
import time
import re

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import tld

from .parse_response import ParseResponse
from . import user_agent


class BaseScrapy(object):

    def __init__(self):
        logging.getLogger(__name__)
        self.proxies = {}
        self.headers = {}
        self.user_agent = ''
        self.skip_ssl_verify = True
        self.change_user_agent_interval = 10
        self.outbound_ip = None
        self.request_attempts = {}
        self.request_count = 0
        self.request_total = 0
        self.last_request_time = None
        self.last_response = None
        self.send_user_agent = ''
        self.max_content_length = 200000000  # Sets the maximum downloard size, default 200 MegaBytes, in bytes.
        self.mininum_wait_time = 0  # Sets the minumum wait time per domain to make a new request in seconds.
        self._setup_proxies()

    def __repr__(self):
        proxy = ''
        if self.proxies.get('http'):
            proxy = " Proxy:%s" % self.proxies.get('http')
        return '<Scrapy%s>' % proxy

    def _make_request(self, url, ssl_verify, attempts, method="GET", payload=None):
        """
        Makes the response, over GET, POST or PUT.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified the request
            will fail.
        :type ssl_verify: bool
        :param attempts: The number of attempts to try before giving up.
        :type attempts: int
        :param method: HTTP verb to use, defaults to GET, can alternatively be POST.
        :type method: str
        :param payload: The payload to be sent, if we're making a post request.
        :type payload: dict
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        ts_start = int(round(time.time() * 1000))
        url = ParseResponse.add_missing_protocol(url)
        attempts = self._request_attempts(url)
        headers = self._set_headers(attempts)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self._increment_counters()
        self._handle_sleep(url)

        try:
            if method == 'GET':
                response = self._make_get(url, headers, payload, ssl_verify)
            elif method == 'POST':
                response = self._make_post(url, headers, payload, ssl_verify)
            elif method == 'PUT':
                response = self._make_put(url, headers, payload, ssl_verify)
        except requests.exceptions.ProxyError:
            logging.warning('Hit a proxy error, sleeping for %s and continuing.')
            time.sleep(4)
            return self._make_request(url, ssl_verify, attempts, method="GET", payload=None)

        self.last_response = response
        ts_end = int(round(time.time() * 1000))
        roundtrip = ts_end - ts_start
        self.last_request_time = datetime.now()
        response.roundtrip = roundtrip
        response.domain = self._get_domain(url)

        if response.status_code >= 503 and response.status_code < 600:
            logging.warning('Recieved an error response %s' % response.status_code)

        logging.debug('Repsonse took %s for %s' % (roundtrip, url))

        return response

    def _make_get(self, url, headers, payload, ssl_verify):
        """
        Makes the GET request and handles different errors that may come about.

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
        try:
            response = requests.get(
                url,
                headers=headers,
                params=payload,
                proxies=self.proxies,
                verify=ssl_verify)
        except requests.exceptions.SSLError:
            logging.warning('Recieved an SSLError from %s' % url)
            if self.skip_ssl_verify:
                logging.warning('Re-running request without SSL cert verification.')
                return self.get(url, skip_ssl_verify=True)
            return self._handle_ssl_error(url, 'GET')
        except requests.exceptions.ConnectionError:
            logging.error('Unabled to connect to: %s' % url)
            raise requests.exceptions.ConnectionError
        return response

    def _make_post(self, url, headers, payload, ssl_verify):
        """
        Makes the POST request and handles different errors that may come about.

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
        try:
            response = requests.post(
                url,
                headers=headers,
                proxies=self.proxies,
                verify=ssl_verify,
                data=payload)
        except requests.exceptions.SSLError:
            return self._handle_ssl_error(url, 'POST', payload)

        return response

    def _make_put(self, url, headers, payload, ssl_verify):
        """
        Makes the PUT request and handles different errors that may come about.

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
        try:
            response = requests.put(
                url,
                headers=headers,
                proxies=self.proxies,
                verify=ssl_verify,
                data=payload)
        except requests.exceptions.SSLError:
            return self._handle_ssl_error(url, 'PUT', payload)

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

        if not self.last_response:
            return

        if tld.get_fld(self.last_response.url) != tld.get_fld(url):
            return

        if not self.last_request_time:
            return

        diff_time = datetime.now() - self.last_request_time
        if diff_time.seconds < self.mininum_wait_time:
            sleep_time = self.mininum_wait_time - diff_time.seconds
            logging.debug('Sleeping %s seconds before next request.')
            time.sleep(sleep_time)

    def _request_attempts(self, url):
        """
        Method to keep track of requests made to a domain and urls. This will likely be wiped everytime we change ips.

        """
        site_domain = self._get_domain(url)

        # Handle the domain portion of requested_attempts.
        if site_domain not in self.request_attempts:
            self.request_attempts[site_domain] = {
                'urls': {},
                'total_requests': 1,
            }
        else:
            self.request_attempts[site_domain]['total_requests'] += 1

        # Handle the URL portion of requested_attemps.
        if url not in self.request_attempts[site_domain]['urls']:
            self.request_attempts[site_domain]['urls'][url] = {
                'count': 1
            }
        else:
            self.request_attempts[site_domain]['urls'][url]['count'] += 1

        return self.request_attempts[site_domain]

    def _get_domain(self, url):
        """
        Tries to get the domain/ip and port from the url we are requesting to.
        @tod: There looks to be an issue with getting an ip address from the url.

        :param url:
        :type urls: str
        :returns: The domain/ip of the server being requested to.
        :rtype: str
        """
        ip_check = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}([:]\d{2,4})?", url)

        try:
            return ip_check.group()
        except AttributeError:
                pass
        if '//localhost' in url:
            return 'localhost'

        try:
            return tld.get_fld(url)
        except tld.exceptions.TldDomainNotFound:
            logging.warning('Could not determin domain for %s' % url)
            return ''

    def _set_headers(self, attempts):
        """
        Sets headers for the request, checks for user values in self.headers and then creates the rest.

        :param attempts: The previous and current info on attempts being made to scrape a domain/url.
        :type attemps: dict
        :param headers: (optional) User/ method base headers to use.
        :type headers: dict
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

        if not self.send_user_agent or self.request_count == self.change_user_agent_interval:
            self.send_user_agent = user_agent.get_random_ua(self.send_user_agent)
            logging.debug('Setting new UA: %s' % self.send_user_agent)
            return

    def _handle_ssl_error(self, url, method, payload):
        """
        Used to catch an SSL issue and allow scrapy to choose whether or not to try without SSL.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param method: HTTP verb to use, only supporting GET and POST currently.
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj or False
        """
        logging.warning("""There was an error with the SSL cert, this happens a lot with LetsEncrypt certificates. Set the class
            var, self.skip_ssl_verify or use the skip_ssl_verify in the .get(url=url, skip_ssl_verify=True)""")
        if self.skip_ssl_verify:
            logging.warning('Re-running request without SSL cert verification.')
            if method == 'GET':
                return self.get(url, payload, skip_ssl_verify=True)
            elif method == 'POST':
                return self.post(url, payload, skip_ssl_verify=True)
            elif method == 'PUT':
                return self.put(url, payload, skip_ssl_verify=True)
        return False

    def _increment_counters(self):
        """
        Add one to each request counter after a request has been made.

        """
        self.request_count += 1
        self.request_total += 1

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
        """
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

# EndFile: scrapy/scrapy/scrapy.py