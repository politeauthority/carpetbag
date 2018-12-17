"""BaseCarpetBag

"""
from datetime import datetime
import json
import logging
import os
import time
import urllib3
from urllib3.exceptions import InsecureRequestWarning

import arrow
import requests
from requests.exceptions import ChunkedEncodingError

from . import carpet_tools
from carpetbag import errors


class BaseCarpetBag(object):

    __version__ = "0.0.2"

    def __init__(self):
        """
        CarpetBag constructor. Here we set the default, user changable class vars.

        :class param headers: Any extra headers to add to the response. This can be maniuplated at any time and applied
            just before each request made.
        :class type headers: dict

        :class param user_agent: User setable User Agent to send on every request. This can be updated at any time.
        :class type user_agent: str

        :class param random_user_agent: Setting to decide whether or not to use a random user agent string.
        :class type random_user_agent: bool

        :class param ssl_verify : Skips the SSL cert verification if set False. Sometimes this is needed when hitting
            certs given out by LetsEncrypt.
        :class type ssl_verify: bool

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

        Everything below is still to be implemented!
        :class param change_user_interval: Changes identity every x requests. @todo: Implement the changing.

        :class param username: User name to use when needing to authenticate a request. @todo Authentication needs to
            be implemented.

        :class param password: Password to use when needing to authenticate a request. @todo Authentication needs to
            be implemented.

        :class param auth_type: Authentication class to use when needing to authenticate a request. @todo
            Authentication needs to be implemented.
        """
        self.headers = {}
        self.user_agent = "CarpetBag v%s" % self.__version__
        self.random_user_agent = False
        self.mininum_wait_time = 0  # Sets the minumum wait time per domain to make a new request in seconds.
        self.wait_and_retry_on_connection_error = 0
        self.retries_on_connection_failure = 5
        self.max_content_length = 200000000  # Sets the maximum downloard size, default 200 MegaBytes, in bytes.
        self.username = None
        self.password = None
        self.auth_type = None
        self.change_identity_interval = 0
        self.remote_service_api = "https://www.bad-actor.services/api"

        # These are private reserved class vars, don"t use these!
        self.outbound_ip = None
        self.request_count = 0
        self.request_total = 0
        self.last_request_time = None
        self.last_response = None
        self.manifest = []
        self.proxy = {}
        self.proxy_bag = []
        self.random_proxy_bag = False
        self.send_user_agent = ""
        self.ssl_verify = True
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        proxy = ""
        if self.get("http"):
            proxy = " Proxy:%s" % self.proxy.get("http")
        else:
            proxy = " Proxy:%s" % self.proxy.get("https")

        return "<CarpetBag%s>" % proxy

    def _make_request(self, method, url, payload={}):
        """
        Makes the URL request, over your choosen HTTP verb.

        :param method: The method for the request action to use. "GET", "POST", "PUT", "DELETE"
        :type method: string
        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The payload to be sent, if we"re making a post request.
        :type payload: dict
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        ts_start = int(round(time.time() * 1000))
        url = carpet_tools.add_missing_protocol(url)
        headers = self._get_headers()
        urllib3.disable_warnings(InsecureRequestWarning)
        self._start_new_manifest(method, url, payload)
        self._increment_counters()
        self._handle_sleep(url)

        response = self._make(method, url, headers, payload)

        if response.status_code >= 500:
            self.logger.warning("Recieved a server error response %s" % response.status_code)

        roundtrip = self._after_request(ts_start, url, response)
        self._end_manifest(response, roundtrip)
        self.logger.debug("Repsonse took %s for %s" % (roundtrip, url))

        return response

    def _handle_sleep(self, url):
        """
        Sets CarpetBag to sleep if we are making a request to the same server in less time then the value of
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
        if self.last_response.domain != carpet_tools.get_domain(url):
            return

        # Checks the time of the last request and sets the sleep timer for the difference.
        diff_time = datetime.now() - self.last_request_time
        if diff_time.seconds < self.mininum_wait_time:
            sleep_time = self.mininum_wait_time - diff_time.seconds
            self.logger.debug("Sleeping %s seconds before next request.")
            time.sleep(sleep_time)

        return True

    def _get_headers(self):
        """
        Gets headers for the request, checks for user values in self.headers and then creates the rest.

        :returns: The headers to be sent in the request.
        :rtype: dict
        """
        send_headers = {}
        self._set_user_agent()
        if self.send_user_agent:
            send_headers["User-Agent"] = self.send_user_agent

        for key, value in self.headers.items():
            send_headers[key] = value

        return send_headers

    def _validate_continents(self, requested_continents):
        """
        Checks that the user selected continents are usable strings, not just some garbage.

        :param requested_continents: User selected list of continents.
        :type requested_continents: list
        :returns: Success if supplied continent list is valid.
        :rtype: bool
        :raises: carpetbag.errors.InvalidContinent
        """
        valid_continents = ["North America", "South America", "Asia", "Europe", "Africa", "Austrailia", "Antarctica"]
        for continent in requested_continents:
            if continent not in valid_continents:
                self.logger.error("Unknown continent: %s" % continent)
                raise errors.InvalidContinent(continent)
        return True

    def _set_user_agent(self):
        """
        Sets a user agent to the class var if it is being used, otherwise if it"s the 1st or 10th request, fetches a new
        random user agent string.

        :returns: The user agent string to be used in the request.
        :rtype: str
        """
        if self.user_agent:
            self.send_user_agent = self.user_agent

        return True

    def _fmt_request_args(self, method, headers, url, payload={}, retry=0, internal=False):
        """
        Formats args to be sent to the requests.request()

        :param method: HTTP verb to use.
        :type method: str
        :param headers: The headers to be sent on the request.
        :type: headers: dict
        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :param retry: The current attempt number for the request.
        :type retry: int
        :param internal: Set True if hitting a bad-actor.services API, this will disable SSL certificate verification.
        :type internal: bool
        :returns: Formatted arguments to send to the Requests module.
        :rtype: dict
        """
        request_args = {
            "method": method,
            "url": url,
            "headers": headers,
        }

        if internal:
            request_args["verify"] = False
        else:
            if retry == 0:
                request_args["verify"] = True
            else:
                request_args["verify"] = self.ssl_verify

        # Setup Proxy if we have one.
        if self.proxy:
            request_args["proxies"] = self.proxy

        # Setup payload if we have it.
        if payload:
            if method == "GET":
                request_args["params"] = payload
            elif method in ["PUT", "POST"]:
                request_args["data"] = payload

        return request_args

    def _make(self, method, url, headers, payload={}, retry=0):
        """
        Just about every CarpetBag requesmisct comes through this method. It makes the request and handles different
        errors that may come about.
        @todo: rework arg list to be url, payload, method,

        self.wait_and_retry_on_connection_error can be set to add a wait and retry in seconds.

        :param method: HTTP verb to use.
        :type method: str
        :param url: The url to fetch/ post to.
        :type: url: str
        :param headers: The headers to be sent on the request.
        :type: headers: dict
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :param retry: The current attempt number for the request.
        :type retry: int
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj
        """
        self.logger.debug("Making request: %s" % url)

        request_args = self._fmt_request_args(
            method=method,
            headers=headers,
            url=url,
            payload=payload,
            retry=retry)

        try:
            response = requests.request(**request_args)

        # Catch Connection Refused Error. This is probably happening because of a bad proxy.
        # Catch an error with the connection to the Proxy
        except requests.exceptions.ProxyError:
            if self.random_proxy_bag:
                self.logger.warning("Hit a proxy error, picking a new one from proxy bag and continuing.")
                self.reset_proxy_from_bag()
            else:
                self.logger.warning("Hit a proxy error, sleeping for %s and continuing." % 5)
                time.sleep(5)

            retry += 1
            return self._make(method, url, headers, payload, retry)

        # Catch an SSLError, seems to crop up with LetsEncypt certs.
        except requests.exceptions.SSLError:
            logging.warning("Recieved an SSL Error from %s" % url)
            if not self.ssl_verify:
                logging.warning("Re-running request without SSL cert verification.")
                retry += 1

                return self._make(method, url, headers, payload, retry)
            else:
                msg = """There was an error with the SSL cert, this happens a lot with LetsEncrypt certificates. Use the """
                msg += """carpetbag.use_skip_ssl_verify() method to enable skipping of SSL Certificate checks"""
                logging.error(msg)
                raise requests.exceptions.SSLError

        # Catch the server unavailble exception, and potentially retry if needed.
        except requests.exceptions.ConnectionError:
            retry += 1
            response = self._handle_connection_error(method, url, headers, payload, retry)
            raise requests.exceptions.ConnectionError

        # Catch a ChunkedEncodingError, response when the expected byte size is not what was recieved, probably a
        # bad proxy
        except ChunkedEncodingError:
            if self.random_proxy_bag:
                self.logger.warning("Hit a ChunkedEncodingError, proxy might be running to slow resetting proxy.")
                self.reset_proxy_from_bag()
            else:
                raise ChunkedEncodingError

        return response

    def _make_internal(self, uri_segment, payload={}, page=1):
        """
        Makes requests to bad-actor.services. For getting data like current_ip, proxies and sending usage data if
        enabled and you have an API key.

        :param uri_segment: The url to fetch/ post to.
        :type: uri_segment: str
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :returns: The json response from the remote service API
        :rtype: dict
        """
        # This is a hack because BadActor does not have the IP /api route set up yet.
        if uri_segment == "ip":
            api_url = carpet_tools.url_join(self.remote_service_api.replace("api", "ip"))
        else:
            api_url = carpet_tools.url_join(self.remote_service_api, uri_segment)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CarpetBag v%s" % self.__version__
        }

        # @todo: Break this up into sub methods!
        params = {}
        if uri_segment == "proxies":
            params = {"q": {}}
            if payload:
                params["filters"] = []

                # Add continent filter
                # @todo: Continent filtering is not working currently, looks like an API problem though.
                if payload.get("continent"):
                    filter_continent = {
                        "name": "continent",
                        "op": "eq",
                        "val": payload["continent"]
                    }
                    params["filters"].append(filter_continent)

                # Add ssl filter
                # @todo: SSL filtering is not working currently, looks like an API problem though.
                if payload.get("ssl_only"):
                    filters_ssl = {
                        "name": "ssl",
                        "op": "eq",
                        "ssl": 1
                    }
                    params["filters"].append(filters_ssl)

            params["q"]["order_by"] = {
                "field": "quality",
                "direction": "desc"
            }

            params["q"]["limit"] = 100
            params["q"]["page"] = 1

        request_args = self._fmt_request_args(
            method="GET",
            headers=headers,
            url=api_url,
            payload=json.dumps(params),
            internal=True)

        try:
            response = requests.request(**request_args)
        except requests.exceptions.ConnectionError:
            raise errors.NoRemoteServicesConnection("Cannot connect to bad-actor.services API")

        return response.json()

    def _handle_connection_error(self, method, url, headers, payload, retry):
        """
        Handles a connection error. If self.wait_and_retry_on_connection_error has a value other than 0 we will wait
        that long until attempting to retry the url again.

        :param url: The url to fetch/ post to.
        :type: url: str
        :param headers: The headers to be sent on the request.
        :type: headers: dict
        :param payload: The data to be sent over the POST request.
        :type payload: dict
        :param retry: Number of attempts that have already been performed for this request.
        :type retry: int
        :returns: A Requests module instance of the response.
        :rtype: <Requests.response> obj or None
        """
        self.logger.error("Unable to connect to: %s" % url)

        if retry > self.retries_on_connection_failure:
            raise requests.exceptions.ConnectionError

        if self.random_proxy_bag:
            self.reset_proxy_from_bag()

        if not self.retries_on_connection_failure:
            raise requests.exceptions.ConnectionError

        # Go to sleep and try again
        self.logger.warning(
            "Attempt %s of %s. Sleeping and retrying url in %s seconds." % (
                str(retry),
                self.retries_on_connection_failure,
                self.wait_and_retry_on_connection_error))
        if self.wait_and_retry_on_connection_error:
            time.sleep(self.wait_and_retry_on_connection_error)

        return self._make(method, url, headers, payload, retry)

    def _after_request(self, ts_start, url, response):
        """
        Runs after request opperations, sets counters and run times. This Should be called before any raised known
        execptions.

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
            print("ROUNDTRIP: %s %s" % (url, roundtrip))
            response.roundtrip = roundtrip
            response.domain = carpet_tools.get_domain(response.url)
        self.ts_start = None

        return roundtrip

    def _increment_counters(self):
        """
        Add one to each request counter after a request has been made.

        """
        self.request_count += 1
        self.request_total += 1

    def _start_new_manifest(self, method, url, payload={}):
        """
        Starts a new manifest for the url being requested, and saves it into the self.manifest var.

        :param method: The method for the request action to use. "GET", "POST", "PUT", "DELETE"
        :type method: string
        :param url: The url to fetch/ post to.
        :type: url: str
        :param payload: The payload to be sent, if we"re making a post request.
        :type payload: dict
        :returns: The newly created manifest record.
        :type: dict
        """
        new_manifest = {
            "method": method,
            "url": url,
            "payload_size ": 0,
            "date_start": arrow.utcnow(),
            "date_end": None,
            "roundtrip": None,
            "response": None,
            "retry": 0,
            "errors": []
        }
        self.manifest.insert(0, new_manifest)
        return new_manifest

    def _end_manifest(self, response, roundtrip):
        """
        Ends the manifest for a requested url with endtimes and runtimes.

        :param response: The response pulled from the request.
        :rtype response: <Response> obj
        :param roundtrip: The time it took to get the response.
        :type roundtrip: float
        :returns: True if everything worked.
        :type: bool
        """
        self.manifest[0]["date_end"] = arrow.utcnow()
        self.manifest[0]["roundtrip"] = roundtrip

        return True

    def _prep_destination(self, destination):
        """
        Attempts to create the destintion directory path if needed.

        :param destination:
        :type destination: str
        :returns: Success or failure of pepping destination.
        :rtype: bool
        """
        if os.path.exists(destination):
            return True

        try:
            os.makedirs(destination)
            return True
        except Exception:
            self.logger.error("Could not create directory: %s" % destination)
            return False

    def _content_type_to_extension(self, content_type):
        """
        Takes a content type and tries to map it to an extension.
        @todo: Needs unit test.

        :param content_type: Content type from a request
        :type content_type: str
        :returns: The extension translation from the content-type.
        :rtype: str
        """
        if content_type == "image/jpg":
            return "jpg"
        return ""

# EndFile: carpetbag/carpetbag/base_carpetbag.py
