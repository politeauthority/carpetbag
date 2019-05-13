"""Test CarpetBag's public methods that are not the basic HTTP verbs.

"""
from datetime import datetime
import os
import re

import requests
import pytest

from carpetbag import CarpetBag
from carpetbag import errors
from carpetbag import carpet_tools as ct

TOR_PROXY_CONTAINER = os.environ.get("TOR_PROXY_CONTAINER", "tor")
# UNIT_TEST_URL = os.environ.get("BAD_ACTOR_URL", "https//bas.bitgel.com")
UNIT_TEST_URL = "https://bas.bitgel.com"
UNIT_TEST_URL_BROKEN = "http://0.0.0.0:90/"
UNIT_TEST_AGENT = "CarpetBag v%s/ UnitTests" % CarpetBag.__version__


class TestPublic(object):

    def test_get(self):
        """
        Tests the CarpetBag.get() method and some of the many different ways that it can be used.

        """
        bagger = CarpetBag()
        bagger.mininum_wait_time = 50
        bagger.retries_on_connection_failure = 0
        bagger.use_skip_ssl_verify(force=True)
        bagger.user_agent = UNIT_TEST_AGENT
        bagger.remote_service_api = UNIT_TEST_URL

        first_successful_response = bagger.get(UNIT_TEST_URL)
        bagger.get(ct.url_join(UNIT_TEST_URL, "api/proxies"))

        assert self._run_get_successful_test(bagger, first_successful_response)
        assert self._run_inspect_manifest(bagger)

        assert self._run_unabled_to_connect(bagger)

    def _run_get_successful_test(self, bagger, successful_response):
        """
        Tests CarpetBag.get() to make sure a successful response sets and returns everything that it should.

        :param bagger: The current CarpetBag instance running through the test.
        :type bagger: <CarpetBag> obj
        :returns: Returns True if everything works.
        :rtype: bool
        """
        assert successful_response
        assert successful_response.status_code == 200
        assert isinstance(bagger.last_request_time, datetime)
        assert bagger.user_agent == UNIT_TEST_AGENT

        return True

    def _run_inspect_manifest(self, bagger):
        """

        :param bagger: The current CarpetBag instance running through the test.
        :type bagger: <CarpetBag> obj
        :returns: Returns True if everything works.
        :rtype: bool
        """
        assert isinstance(bagger.manifest, list)
        assert len(bagger.manifest) == 2
        assert bagger.manifest[0]["method"] == "GET"
        assert bagger.manifest[0]["roundtrip"] > 0
        assert bagger.manifest[0]["attempt_count"] > 0
        assert isinstance(bagger.manifest[0]["errors"], list)
        assert len(bagger.manifest[0]["errors"]) == 0
        assert bagger.manifest[1]["url"] == UNIT_TEST_URL

        return True

    def _run_unabled_to_connect(self, bagger):
        """
        Tests Carpetbag().get() handling of ConnectionErrors

        :param bagger: The current CarpetBag instance running through the test.
        :type bagger: <CarpetBag> obj
        :returns: Returns True if everything works.
        :rtype: bool
        """
        with pytest.raises(requests.exceptions.ConnectionError):
            bagger.get(UNIT_TEST_URL_BROKEN)
        
        return True

    def test_use_random_user_agent(self):
        """
        Tests CarpetBag.use_random_user_agent()

        """
        bagger = CarpetBag()
        assert bagger.user_agent == "CarpetBag v%s" % bagger.__version__
        bagger.user_agent = UNIT_TEST_AGENT
        assert bagger.user_agent == UNIT_TEST_AGENT
        assert not bagger.random_user_agent

        assert bagger.use_random_user_agent()  # Turn on random user agent.
        assert bagger.random_user_agent
        assert not bagger.use_random_user_agent(False)
        assert bagger.user_agent == ""

        bagger.use_skip_ssl_verify()
        bagger.get(bagger.remote_service_api)
        assert bagger.send_user_agent == ""  # Test that we send the chosen user agent

    def test_get_new_user_agent(self):
        """
        Tests the CarpetBag().get_new_user_agent() method to make sure gets user agents and does not retry the same user
        agent that is currently being used by CarpetBag.

        """
        bagger = CarpetBag()
        ua_1 = bagger.get_new_user_agent()
        bagger.user_agent = ua_1
        ua_2 = bagger.get_new_user_agent()

        assert isinstance(ua_1, str)
        assert ua_1 != ua_2

    def test_get_public_proxies(self):
        """
        Tests BaseCarpetBag().get_public_proxies()

        """
        bagger = CarpetBag()
        bagger.user_agent = UNIT_TEST_AGENT

        assert not bagger.proxy
        assert isinstance(bagger.proxy_bag, list)
        assert len(bagger.proxy_bag) == 0
        proxies = bagger.get_public_proxies()

        assert isinstance(proxies, list)
        assert len(proxies) > 5
        assert isinstance(bagger.proxy_bag, list)
        assert len(bagger.proxy_bag) > 5

        # Test the continent filtering
        proxies = bagger.get_public_proxies("Asia")
        for proxy in proxies:
            assert proxy["continent"] == "Asia"
        proxies = bagger.get_public_proxies("North America")
        for proxy in proxies:
            assert proxy["continent"] == "North America"

        # Test that we raise a No Remote Services Connection error when we can reach Bad-Actor
        bagger.remote_service_api = UNIT_TEST_URL_BROKEN
        with pytest.raises(errors.NoRemoteServicesConnection):
            bagger.get_public_proxies()

    # def test_use_random_public_proxy(self):
    #     """
    #     Tests BaseCarpetBag().use_public_proxies()

    #     """
    #     bagger = CarpetBag()
    #     bagger.user_agent = UNIT_TEST_AGENT

    #     assert not bagger.proxy
    #     assert isinstance(bagger.proxy, dict)
    #     assert not bagger.random_proxy_bag
    #     assert not bagger.proxy_bag
    #     assert isinstance(bagger.proxy_bag, list)

    #     no_proxy_ip = bagger.get_outbound_ip()

    #     assert bagger.use_random_public_proxy()
    #     assert bagger.random_proxy_bag
    #     assert len(bagger.proxy) > 0
    #     assert "http" in bagger.proxy or "https" in bagger.proxy
    #     current_ip = bagger.get_outbound_ip()

    #     # @todo: The ip check is not currently working. Need to fix!
    #     assert no_proxy_ip != current_ip

    #     assert bagger.use_random_public_proxy(test_proxy=True)

    def test_use_skip_ssl_verify(self):
        """
        Tests CarpetBag().use_ssl_verify() to make sure if sets and uses the value CarpetBag.ssl_verify

        """
        bagger = CarpetBag()
        assert bagger.ssl_verify
        assert bagger.use_skip_ssl_verify()
        assert not bagger.ssl_verify
        assert not bagger.use_skip_ssl_verify(False)
        assert bagger.ssl_verify

    # def test_save(self):
    #     """
    #     Tests the CarpetBag.save() method to make sure it can download files.
    #     """
    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify()

    #     image_1_url = ct.url_join(bagger.remote_service_api.replace("api", ""), "test/troll.jpg")

    #     # Test the file being named after the full path given in the destination.
    #     saved_phile_name = bagger.save(
    #         image_1_url,
    #         "/opt/carpetbag/tests/data/images/test_download.jpg")

    #     assert saved_phile_name
    #     assert saved_phile_name == "/opt/carpetbag/tests/data/images/test_download.jpg"
    #     os.remove(saved_phile_name)

    #     # Test the name of the file being the last url segment
    #     saved_phile_name = bagger.save(
    #         image_1_url,
    #         "/opt/carpetbag/tests/data/images/")
    #     assert saved_phile_name
    #     assert saved_phile_name == "/opt/carpetbag/tests/data/images/troll.jpg"
    #     os.remove(saved_phile_name)

    #     # Test that we respect the overwrite argument
    #     with pytest.raises(errors.CannotOverwriteFile):
    #         bagger.save(


    #             image_1_url,
    #             "/opt/carpetbag/tests/data/images/existing.jpg")

    # def test_search(self):
    #     """
    #     Tests CarpetBag().search(), which runs a search on DuckDuckGo and parses the response.
    #     @note: If this test refetches data its very likely this test can fail, beware!

    #     """
    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify(force=True)
    #     response = bagger.search("learn python")
    #     assert response["results"][0]["title"] == "Learn Python - Free Interactive Python Tutorial"

    # def test_check_tor(self):
    #     """
    #     Tests the method CarpetBag().check_tor(), this test mocks out a failure of connecting to tor.

    #     """
    #     bagger = CarpetBag()
    #     bagger.retries_on_connection_failure = 0
    #     tor_1 = bagger.check_tor()

    #     bagger.proxy["https"] = "https://%s:8119" % TOR_PROXY_CONTAINER
    #     tor_2 = bagger.check_tor()
    #     assert not tor_1
    #     assert tor_2

    # def test_parse(self):
    #     """
    #     Tests the CarpetBag().parse() method to make sure we're returning the correct object back.

    #     """
    #     bagger = CarpetBag()
    #     bagger.user_agent = UNIT_TEST_AGENT
    #     bagger.use_skip_ssl_verify(force=True)
    #     bagger.get(UNIT_TEST_URL)

    def test_get_outbound_ip(self):
        """
        Tests the CarpetBag().get_outbound_ip method to make sure we get and parse the outbound IP correctly.

        """
        bagger = CarpetBag()
        ip = bagger.get_outbound_ip()
        assert re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)  # Something to the tune of "184.153.235.188"
        assert re.match(
            r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
            bagger.outbound_ip)  # Something to the tune of "184.153.235.188"

    # def test_reset_identity(self):
    #     """
    #     Tests the CarpetBag().reset_identity() method, makeing sure:
    #         - We reset the User-Agent if the use_random_user_agent() method has been invoked.
    #         - We pick a new proxy if the use_random_public_proxy() method has been invoked.

    #     """
    #     bagger = CarpetBag()
    #     bagger.use_random_user_agent()
    #     bagger.use_random_public_proxy()

    #     first_ip = bagger.get_outbound_ip()
    #     first_ua = bagger.user_agent
    #     first_proxy = bagger.proxy
    #     bagger.reset_identity()

    #     second_ip = bagger.get_outbound_ip()

    #     assert first_ua != bagger.user_agent
    #     assert first_proxy != bagger.proxy
    #     assert first_ip != second_ip

    def test_set_header(self):
        """
        Tests the CarpetBag().set_header() method to make sure it adds the headers to the CarpetBag.header class var.

        """
        bagger = CarpetBag()
        assert isinstance(bagger.set_header("Test-Header", "Test Header Value"), dict)
        assert bagger.headers.get("Test-Header") == "Test Header Value"

    # def test_set_header_once(self):
    #     """
    #     Tests the CarpetBag().test_set_header_once() method to make sure it adds the headers to the CarpetBag.header
    #     class var and then removes it after a request has been made.

    #     """
    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify(force=True)

    #     bagger.set_header_once("Test-Header", "Test Header Value")
    #     assert "Test-Header" in bagger.one_time_headers
    #     assert bagger.headers.get("Test-Header") == "Test Header Value"

    #     bagger.get(UNIT_TEST_URL)
    #     assert not bagger.headers.get("Test-Header")


# End File carpetbag/tests/test_public.py
