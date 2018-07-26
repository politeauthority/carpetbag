"""Scrapy

"""
from datetime import datetime
import logging
import os
import time

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import tld


from .parse_response import ParseResponse
from . import user_agent


class Scrapy(object):

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
        self.last_request = None
        self.send_user_agent = ''
        self._setup_proxies()

    def __repr__(self):
        proxy = ''
        if self.proxies.get('http'):
            proxy = " Proxy:%s" % self.proxies.get('http')
        return '<Scrapy%s>' % proxy

    def get(self, url, skip_ssl_verify=False):
        """
        Wrapper for the Requests python module's get method, adds in extras such as headers and proxies where
        applicable.

        :param url: The url to fetch.
        :type: url: str
        :param skip_ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified will continue.
        :type skip_ssl_verify: bool
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        ssl_verify = True
        if skip_ssl_verify:
            ssl_verify = False
        headers = {}
        response = self._make_request(url, ssl_verify, headers, 5)

        return response

    def post(self, url, payload, skip_ssl_verify=False):
        """
        Wrapper for the Requests python module's get method, adds in extras such as headers and proxies where
        applicable.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The data to be sent over POST.
        :type payload: dict
        :param skip_ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified will continue.
        :type skip_ssl_verify: bool
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        ssl_verify = True
        if skip_ssl_verify:
            ssl_verify = False
        headers = {}
        response = self._make_request(url, ssl_verify, headers, 5)
        return response

    def save(self, url, destination, skip_ssl_verify=True):
        """
        Saves a file to a destination on the local drive. Good for quickly grabbing images from a remote site.
        @todo: impelement the content size restriction.

        :param url: The url to fetch.
        :type: url: str
        :param destination: Where on the local filestem to store the image.
        :type: destination: str
        :param skip_ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified will continue.
        :type skip_ssl_verify: bool
        """
        h = requests.head(url, allow_redirects=True)
        header = h.headers
        content_type = header.get('content-type')
        if 'text' in content_type.lower():
            return False
        if 'html' in content_type.lower():
            return False

        # content_length = header.get('content-length', None)
        # if content_length and content_length > 2e8:  # 200 mb approx
        #     return False

        save_dir = self._find_destination(destination)
        response = self.get(url, skip_ssl_verify=skip_ssl_verify)
        phile_name = url[url.rfind('/') + 1:]
        full_phile_name = os.path.join(save_dir, phile_name)
        print(full_phile_name)
        open(full_phile_name, 'wb').write(response.content)
        return full_phile_name

    def search(self, query, engine='duckduckgo'):
        """
        Runs a search query on a search engine with the current proxy, and returns a parsed result set.
        Currently only engine supported is duckduckgo.

        :param query: The query to run against the search engine.
        :type query: str
        :param engine: Search engine to use, default 'duckduckgo'.
        :type engine: str
        :returns: The results from the search engine.
        :rtype: dict
        """
        search = self.get("https://duckduckgo.com/?q=%s&ia=web" % query)
        results = ParseResponse(search).duckduckgo_results()
        ret = {
            'request': search,
            'query': query,
            'results': results
        }
        return ret

    def check_tor(self):
        """
        Checks the Tor Projects page "check.torproject.org" to see if we're running through a tor proxy correctly, and
        exiting through an actual tor exit node.

        """
        response = self.get('https://check.torproject.org')
        parsed = ParseResponse(response)
        return parsed.get_title()

    def get_outbound_ip(self):
        """
        Gets the currentoutbound IP address for scrappy and sets the self.outbound_ip var.

        :returns: The outbound ip address for the proxy.
        :rtype: str
        """
        ip_websites = ['http://icanhazip.com/']
        for ip in ip_websites:
            response = self.get(ip)
            if response.status_code != 200:
                logging.warning('Unable to connect to %s for IP.')
                continue

            if response.text != self.outbound_ip:
                self.outbound_ip = response.text
            return self.outbound_ip

        self.log.error('Could not get outbound ip address.')
        return False

    def _make_request(self, url, ssl_verify, headers, attempts, method="GET", payload=None):
        """
        Makes the response, over GET or POST.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified the request
            will fail.
        :type ssl_verify: bool
        :param headers: Request headers to be sent, such as user agent and whatever else you got.
        :type headers: dict
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
        headers = self._set_headers(attempts, headers)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self._increment_counters()

        if method == 'GET':
            response = self._make_get(url, headers, ssl_verify)
        elif method == 'POST':
            response = self._make_post(url, headers, ssl_verify, payload)


        ts_end = int(round(time.time() * 1000))
        roundtrip = ts_end - ts_start
        self.last_request = datetime.now()
        response.roundtrip = roundtrip

        if response.status_code >= 503 and response.status_code < 600:
            logging.warning('Recieved an error response %s' % response.status_code)

        logging.debug('Repsonse took %s for %s' % (roundtrip, url))

        return response

    def _make_get(self, url, headers, ssl_verify):
        """

        :param url: The url to fetch/ post to.
        :type: url: str
        :param headers: Request headers to be sent, such as user agent and whatever else you got.
        :type headers: dict
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
                proxies=self.proxies,
                verify=ssl_verify)
        except requests.exceptions.SSLError:
            logging.warning('Recieved an SSLError from %s' % url)
            if self.skip_ssl_verify:
                logging.warning('Re-running request without SSL cert verification.')
                return self.get(url, skip_ssl_verify=True)
            return self._handle_ssl_error(url, 'GET')

        return response

    def _make_post(self, url, headers, ssl_verify, payload):
        """

        :param url: The url to fetch/ post to.
        :type: url: str
        :param headers: Request headers to be sent, such as user agent and whatever else you got.
        :type headers: dict
        :param ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified the request
            will fail.
        :type ssl_verify: bool
        :param payload: The data to be sent over the POST request.
        :type payload: dict
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

    def _request_attempts(self, url):
        """
        Method to keep track of requests made to a domain and urls. This will likely be wiped everytime we change ips.

        """
        # Handle the domain portion of requested_attempts.
        site_domain = tld.get_tld(url)
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

    def _set_headers(self, attempts, headers={}):
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
        if 'User-Agent' in attempts:
            send_headers['User-Agent'] = attempts['User-Agent']
        else:
            send_headers['User-Agent'] = self.send_user_agent

        for key, value in headers.items():
            send_headers[key] = value

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
        return False

    def _increment_counters(self):
        """
        Add one to each request counter after a request has been made.

        """
        self.request_count += 1
        self.request_total += 1

    def _find_destination(self, destination):
        if os.path.exists(os.path.isdir(destination)):
            return destination
        elif os.path.exists(destination):
            print(destination)


# EndFile: scrapy/scrapy/scrapy.py
