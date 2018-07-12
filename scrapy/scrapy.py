"""Scrapy

"""
import logging

import requests
import tld

from .parse_response import ParseResponse


class Scrapy(object):

    def __init__(self):
        logging.getLogger(__name__)
        self.proxies = {}
        self.headers = {}
        self.skip_ssl_verify = True
        self.outbound_ip = None
        self.request_attempts = {}
        self._setup_proxies()

    def __repr__(self):
        return '<Scrapy Proxy:%s>' % self.proxies.get('http')

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
        headers = {'User-Agent': self._set_user_agent()}
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
        headers = {'User-Agent': self._set_user_agent()}
        response = self._make_request(url, ssl_verify, headers, 5)
        return response

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
        :param skip_ssl_verify: If True will attempt to verify a site's SSL cert, if it can't be verified will continue.
        :type skip_ssl_verify: bool
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
        url = ParseResponse.add_missing_protocol(url)
        attempts = self._request_attempts(url)
        headers = self._set_headers(attempts)
        if method == 'GET':
            try:
                # Try to grab the url verifying the SSL certificate first.
                response = requests.get(
                    url,
                    headers=headers,
                    proxies=self.proxies,
                    verify=ssl_verify)
            except requests.exceptions.SSLError:
                if self.skip_ssl_verify:
                    return self.get(url, skip_ssl_verify=True)
                return self._handle_ssl_error()
        elif method == 'POST':
            try:
                # Try to grab the url verifying the SSL certificate first.
                response = requests.post(
                    url,
                    headers=headers,
                    proxies=self.proxies,
                    verify=ssl_verify,
                    data=payload)
            except requests.exceptions.SSLError:
                if self.skip_ssl_verify:
                    return self.post(url, payload, skip_ssl_verify=True)
                return self._handle_ssl_error()

        if response.status_code == 200:
            return response

        if response.status_code in [503]:
            print('we got an error')  # @todo log this.
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

    def _set_headers(self, attempts):
        """
        Sets headers for the request, checks for user values in self.headers and then creates the rest.

        """
        send_headers = {}
        if 'User-Agent' in attempts:
            send_headers['User-Agent'] = attempts['User-Agent']
        else:
            send_headers['User-Agent'] = self._set_user_agent()

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
        return "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"

    def _handle_ssl_error(self):
        logging.warning("""There was an error with the SSL cert, this happens a lot with LetsEncrypt certificates. Set the class
            var, self.skip_ssl_verify or use the skip_ssl_verify in the .get(url=url, skip_ssl_verify=True)""")
        return False

# EndFile: scrapy/scrapy/scrapy.py
