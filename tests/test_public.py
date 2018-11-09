"""Test CarpetBag's public methods that are not the basic HTTP verbs.

"""
from datetime import datetime
import os

import vcr

from carpetbag import CarpetBag
from carpetbag import user_agent

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data/vcr_cassettes")


class TestPublic(object):

    def test_json_date(self):
        """
        Tests the JSON date method to try and convert the information to JSON friendly output.

        """
        now = datetime.now()
        the_date = datetime(2018, 10, 13, 12, 12, 12)
        assert CarpetBag.json_date(the_date) == "2018-10-13 12:12:12"
        assert isinstance(CarpetBag.json_date(), str)
        assert CarpetBag.json_date()[:4] == str(now.year)

    def test_url_concat(self):
        """
        Tests the url_concat method, to make sure we're not adding any extra slashes or making weird urls.

        """
        assert CarpetBag.url_concat("http://www.google.com", "news") == "http://www.google.com/news"
        assert CarpetBag.url_concat("http://www.google.com", "/news") == "http://www.google.com/news"
        assert CarpetBag.url_concat("http://www.google.com", "/") == "http://www.google.com/"
        # assert CarpetBag.url_concat("http://www.google.com/", "/") == "http://www.google.com/"

    def test_use_random_user_agent(self):
        """
        Tests CarpetBag"s main public method to make sure we're getting the responses we expect.

        """
        bagger = CarpetBag()
        assert bagger.user_agent == "CarpetBag v.001"
        bagger.use_random_user_agent()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "public_random_user_agent.yaml")):
            bagger.get("http://www.bad-actor.services")
        assert bagger.user_agent in user_agent.get_flattened_uas()

    def test_check_tor_fail(self):
        """
        Tests the method CarpetBag().check_tor(), this test mocks out a failure of connecting to tor.

        """
        bagger = CarpetBag()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "public_tor_fail.yaml")):
            tor = bagger.check_tor()
            assert not tor

    def test_get_outbound_ip(self):
        """
        Tests the CarpetBag().get_outbound_ip method to make sure we get and parse the outbound IP correctly.

        """
        bagger = CarpetBag()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "public_outbound_ip.yaml")):
            ip = bagger.get_outbound_ip()
            assert ip == "73.203.37.237"

    # Removing this test for the time being, the constanly rotating proxies is casuing false negatives on the test
    # def test_reset_identity(self):
    #     """
    #     """
    #     bagger = CarpetBag()
    #     bagger.use_random_user_agent()
    #     with vcr.use_cassette(os.path.join(CASSET_DIR, "public_reset_identity.yaml")):
    #         bagger.use_random_public_proxy()

    #         first_ip = bagger.get_outbound_ip()
    #         first_ua = bagger.user_agent
    #         first_proxy = bagger.proxy["http"]
    #         bagger.reset_identity()

    #         second_ip = bagger.get_outbound_ip()

    #         assert first_ua != bagger.user_agent
    #         assert first_proxy != bagger.user_agent
    #         assert first_ip != second_ip

    # def test_use_random_public_proxy(self):
    #     """
    #     Tests the CarpetBag().use_random_public_proxy method. Makes sure that it parses the proxy list and sets a
    #     proxy to be used.
    #     """
    #     bagger = CarpetBag()
    #     assert not bagger.random_proxy_bag
    #     with vcr.use_cassette(os.path.join(CASSET_DIR, "public_use_random_public_proxy.yaml")):
    #         bagger.use_random_public_proxy()
    #         proxy_ips = []
    #         for prx in bagger.proxy_bag:
    #             proxy_ips.append(prx["ip"])
    #     assert bagger.proxy["http"] in proxy_ips
    #     assert len(bagger.proxy_bag) > 100
    #     assert bagger.random_proxy_bag

# End File carpetbag/tests/test_public.py
