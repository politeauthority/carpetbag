"""Test CarpetBag's public methods that are not the basic HTTP verbs.

"""
import os
import re

import pytest

from carpetbag import CarpetBag
from carpetbag import user_agent
from carpetbag import errors
from carpetbag import carpet_tools as ct

UNIT_TEST_URL = os.environ.get('BAD_ACTOR_URL', 'https//www.bad-actor.services/')
UNIT_TEST_URL_BROKEN = "http://0.0.0.0:90/"
UNIT_TEST_AGENT = "CarpetBag v%s/ UnitTests" % CarpetBag.__version__


class TestPublic(object):

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
        assert bagger.user_agent in user_agent.get_flattened_uas()  # Check that the user agent is a random one.
        assert not bagger.use_random_user_agent(False)
        assert bagger.user_agent == ""

        bagger.use_skip_ssl_verify()
        bagger.get(bagger.remote_service_api)
        assert bagger.send_user_agent == ""  # Test that we send the chosen user agent

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
        # @todo: Continent filtering is not working currently, looks like an API problem though.
        # proxies = bagger.get_public_proxies("Asia")
        # for proxy in proxies:
        #     assert proxy["continent"] == "Asia"

        # Test the SSL filtering
        # @todo: SSL filtering is not working currently, looks like an API problem though.
        # proxies = bagger.get_public_proxies(ssl_only=True)
        # for proxy in proxies:
        #     assert proxy["ssl"]

        # Test that we raise a No Remote Services Connection error when we can reach Bad-Actor
        bagger.remote_service_api = "http://0.0.0.0:90/"
        with pytest.raises(errors.NoRemoteServicesConnection):
            bagger.get_public_proxies()

    def test_use_random_public_proxy(self):
        """
        Tests BaseCarpetBag().use_public_proxies()

        """
        bagger = CarpetBag()
        bagger.user_agent = UNIT_TEST_AGENT

        assert not bagger.proxy
        assert isinstance(bagger.proxy, dict)
        assert not bagger.random_proxy_bag
        assert not bagger.proxy_bag
        assert isinstance(bagger.proxy_bag, list)

        no_proxy_ip = bagger.get_outbound_ip()

        assert bagger.use_random_public_proxy()
        assert bagger.random_proxy_bag
        assert len(bagger.proxy) > 0
        assert 'http' in bagger.proxy or 'https' in bagger.proxy
        current_ip = bagger.get_outbound_ip()

        # @todo: The ip check is not currently working. Need to fix!
        assert no_proxy_ip != current_ip

        assert bagger.use_random_public_proxy(test_proxy=True)

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

    def test_save(self):
        """
        Tests the CarpetBag.save() method to make sure it can download files.
        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()

        image_1_url = ct.url_join(bagger.remote_service_api.replace("api", ""), "test/troll.jpg")

        # Test the file being named after the full path given in the destination.
        saved_phile_name = bagger.save(
            image_1_url,
            "/opt/carpetbag/tests/data/images/test_download.jpg")

        assert saved_phile_name
        assert saved_phile_name == "/opt/carpetbag/tests/data/images/test_download.jpg"
        os.remove(saved_phile_name)

        # Test the name of the file being the last url segment
        saved_phile_name = bagger.save(
            image_1_url,
            "/opt/carpetbag/tests/data/images/")
        assert saved_phile_name
        assert saved_phile_name == "/opt/carpetbag/tests/data/images/troll.jpg"
        os.remove(saved_phile_name)

        # Test that we respect the overwrite argument
        with pytest.raises(errors.CannotOverwriteFile):
            bagger.save(
                image_1_url,
                "/opt/carpetbag/tests/data/images/existing.jpg")

    def test_search(self):
        """
        Tests CarpetBag().search(), which runs a search on DuckDuckGo and parses the response.
        @note: If this test refetches data its very likely this test can fail, beware!

        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()
        response = bagger.search('learn python')
        assert response['results'][0]['title'] == 'Learn Python - Free Interactive Python Tutorial'

    def test_check_tor(self):
        """
        Tests the method CarpetBag().check_tor(), this test mocks out a failure of connecting to tor.

        """
        bagger = CarpetBag()
        tor_1 = bagger.check_tor()
        bagger.proxy["https"] = "https://tor:8118"
        tor_2 = bagger.check_tor()
        assert not tor_1
        assert tor_2

    def test_parse(self):
        """
        Tests the CarpetBag().parse() method to make sure we're returning the correct object back.

        """
        bagger = CarpetBag()
        bagger.user_agent = UNIT_TEST_AGENT
        bagger.use_skip_ssl_verify()
        bagger.get("https://www.bad-actor.services/")

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

    def test_reset_identity(self):
        """
        Tests the CarpetBag().reset_identity() method, makeing sure:
            - We reset the User-Agent if the use_random_user_agent() method has been invoked.
            - We pick a new proxy if the use_random_public_proxy() method has been invoked.

        """
        bagger = CarpetBag()
        bagger.use_random_user_agent()
        bagger.use_random_public_proxy()

        first_ip = bagger.get_outbound_ip()
        first_ua = bagger.user_agent
        first_proxy = bagger.proxy
        bagger.reset_identity()

        second_ip = bagger.get_outbound_ip()

        assert first_ua != bagger.user_agent
        assert first_proxy != bagger.proxy
        assert first_ip != second_ip

# End File carpetbag/tests/test_public.py
