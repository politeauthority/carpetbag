"""Test Base CarpetBag for the private methods of CarpetBag.

"""
from datetime import datetime
import time
import json
import os

import pytest
import vcr

from carpetbag import CarpetBag
from carpetbag import errors

from .data.response_data import GoogleDotComResponse


CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data/vcr_cassettes")


class TestBaseCarpetBag(object):

    def test___init__(self):
        """
        Tests that the module init has correct default values.

        """
        bagger = CarpetBag()
        assert bagger.proxy == {}
        assert bagger.headers == {}
        assert bagger.user_agent == "CarpetBag v.001"
        assert bagger.ssl_verify
        assert bagger.change_identity_interval == 0
        assert not bagger.outbound_ip
        assert bagger.request_attempts == {}
        assert bagger.request_count == 0
        assert bagger.request_total == 0
        assert not bagger.last_request_time
        assert not bagger.last_response
        assert bagger.send_user_agent == ""
        assert bagger.max_content_length == 200000000
        assert bagger.mininum_wait_time == 0
        assert bagger.wait_and_retry_on_connection_error == 0
        assert not bagger.username
        assert not bagger.password
        assert not bagger.auth_type
        assert not bagger.random_proxy_bag
        assert bagger.proxy_bag == []
        assert bagger.manifest == {}

    def test__make_request(self):
        bagger = CarpetBag()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "test__make_request.yaml")):
            request = bagger._make_request("GET", "http://www.google.com/news")
        assert request
        assert request.text
        assert request.status_code == 200

    def test__handle_sleep_1(self):
        """
        Tests the _handle_sleep() method to make sure sleep isnt used if mininum_wait_time is not set.

        """
        bagger = CarpetBag()
        start_1 = datetime.now()
        bagger._handle_sleep("https://www.google.com/")
        end_1 = datetime.now()
        run_time_1 = (end_1 - start_1).seconds
        assert run_time_1 < 3

        bagger = CarpetBag()
        start_2 = datetime.now()
        bagger._handle_sleep("https://www.google.com/")
        end_2 = datetime.now()
        run_time_2 = (end_2 - start_2).seconds
        assert run_time_2 < 3

    def test__handle_sleep_2(self):
        """
        Tests the _handle_sleep() method to make sure sleep is used on the second request, then dropped for the first
        request of a new domain.

        """
        bagger = CarpetBag()
        bagger.mininum_wait_time = 5

        start_1 = datetime.now()
        bagger._handle_sleep("https://www.google.com/")
        end_1 = datetime.now()
        run_time_1 = (end_1 - start_1).seconds
        assert run_time_1 < 3

        start_2 = datetime.now()
        bagger.last_request_time = start_1
        bagger.last_response = GoogleDotComResponse()
        bagger._handle_sleep("https://www.google.com/")
        end_2 = datetime.now()
        run_time_2 = (end_2 - start_2).seconds
        assert run_time_2 >= 4

        start_3 = datetime.now()
        bagger.last_request_time = start_1
        bagger._handle_sleep("https://www.example.com/")
        end_3 = datetime.now()
        run_time_3 = (end_3 - start_3).seconds
        assert run_time_3 < 3

    def test__get_domain(self):
        """
        Tests the BaseCarpetBag._get_domain method to see if it properly picks the domain from a url.

        """
        bagger = CarpetBag()
        assert bagger._get_domain("http://192.168.50.137:5000") == "192.168.50.137"
        assert bagger._get_domain("http://www.google.com") == "google.com"
        assert bagger._get_domain("http://localhost") == "localhost"
        assert bagger._get_domain("http://192.168.1.19:5010") == "192.168.1.19"

    def test__get_headers(self):
        """
        Tests that headers can be set by the CarpetBag application, and by the end-user.

        """
        bagger = CarpetBag()
        bagger.headers = {"Content-Type": "application/html"}
        bagger.user_agent = "Mozilla/5.0 (Windows NT 10.0)"
        set_headers = bagger._get_headers()

        assert isinstance(set_headers, dict)
        assert len(set_headers) == 2
        assert "User-Agent" in set_headers

    def test__setup_proxy(self):
        """
        Tests that proxies are defaulted to http and https if not specified.

        """
        bagger = CarpetBag()
        assert not bagger.proxy
        bagger.proxy = {"http": "localhost:8118"}
        bagger._setup_proxies()
        assert bagger.proxy["https"] == "localhost:8118"
        assert bagger.proxy["http"] == "localhost:8118"

    def test__filter_public_proxies(self):
        """
        Tests the BaseCarpetBag.__filter_public_proxies() method, which filters public proxies CarpetBag is using.
        First assertion makes sure we filter SSL only proxies
        Second assert makes sure we grab proxies only from North America
        Third assertion checks that the first proxies is from North Amercia
        Fourth assertion checks that we order South America after North America

        @todo: This test is passing, but I dont believe it's checking as many points as it needs to be.
        """
        # Load the test proxies
        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_data = open(os.path.join(dir_path, 'data/default_proxy_bag.json')).read()
        test_proxies = json.loads(json_data)

        # Check that we return a list.
        bagger = CarpetBag()
        assert isinstance(bagger._filter_public_proxies(test_proxies, [], False), list)

        # Check that we get only SSL supporting proxies.
        filtered_proxies = bagger._filter_public_proxies(test_proxies, continents=[], ssl_only=True)
        for proxy in filtered_proxies:
            assert proxy['ssl']

        # Check that we can filter proxies based on a single contintent.
        filtered_proxies = bagger._filter_public_proxies(test_proxies, continents=["North America"])
        for proxy in filtered_proxies:
            assert proxy['continent'] == "North America"

        # Check that we can filter proxies based on a multiple contintents.
        filtered_proxies = bagger._filter_public_proxies(test_proxies, continents=["North America", "South America"])
        for proxy in filtered_proxies:
            assert proxy['continent'] in ["North America", "South America"]

        # Check that we grab proxies from multiple continents, ordered appropriately.
        filtered_proxies = bagger._filter_public_proxies(test_proxies, continents=["North America", 'South America'])
        assert filtered_proxies[0]['continent'] == "North America"
        assert filtered_proxies[len(filtered_proxies) - 1]['continent'] == "South America"

        # Test that we raise the InvalidContinent exception if we get a bad continent name.
        with pytest.raises(errors.InvalidContinent):
            filtered_proxies = bagger._filter_public_proxies(test_proxies, continents=["Nortf America"])

    def test__validate_continents(self):
        """
        Tests the BaseCarpetBag._validate_continents() method to make sure we only are using valid contintent names.

        """
        # Load the test proxies
        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_data = open(os.path.join(dir_path, 'data/default_proxy_bag.json')).read()
        test_proxies = json.loads(json_data)

        bagger = CarpetBag()

        # Check that we return True for valid contintents.
        assert bagger._filter_public_proxies(test_proxies, continents=["North America"])
        assert bagger._filter_public_proxies(test_proxies, continents=["North America", "South America"])

        with pytest.raises(errors.InvalidContinent):
            bagger._filter_public_proxies(test_proxies, continents=["Nortf America"])

    def test__set_user_agent_manual(self):
        """
        Tests to make sure _set_user_agent will not override a manually set user_agent.

        """
        bagger = CarpetBag()
        bagger.user_agent = "My test user agent"
        bagger._set_user_agent()
        assert bagger.send_user_agent == "My test user agent"

        bagger.request_count = 2
        bagger.change_user_agent_interval = 2
        bagger._set_user_agent()
        assert bagger.send_user_agent == "My test user agent"

    def test__make_1(self):
        """
        Tests the _make() method of CarpetBag. This is one of the primary methods of CarpetBag, and could always use
        more tests!

        """
        bagger = CarpetBag()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "test__make_1.yaml")):
            response = bagger._make(
                method="GET",
                url="http://www.google.com",
                headers={"Content-Type": "application/html"},
                payload={},
                retry=0)
            assert response
            assert response.status_code == 200
            response = bagger._make(
                method="GET",
                url="http://www.google.com",
                headers={"Content-Type": "application/html"},
                payload={},
                retry=0)
            assert response
            assert response.status_code == 200

    def test_reset_proxy_from_bag(self):
        """
        Tests the reset_proxy_from_bag() method.

        """
        s = CarpetBag()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "reset_proxy_from_bag.yaml")):
            s.use_random_public_proxy()
            original_proxy_bag_size = len(s.proxy_bag)
            http_proxy_1 = s.proxy["http"]
            https_proxy_1 = s.proxy["https"]

            s.reset_proxy_from_bag()
            http_proxy_2 = s.proxy["http"]
            https_proxy_2 = s.proxy["https"]

            assert http_proxy_1 != http_proxy_2
            assert https_proxy_1 != https_proxy_2
            assert original_proxy_bag_size - 1 == len(s.proxy_bag)

            # If proxy bag is empty, make sure we throw the error
            with pytest.raises(errors.EmptyProxyBag):
                s.proxy_bag = []
                s.reset_proxy_from_bag()

    def test__after_request(self):
        """
        """
        fake_start = int(round(time.time() * 1000)) - 5000
        bagger = CarpetBag()
        bagger._after_request(fake_start, "https://www.google.com", GoogleDotComResponse())

    def test__increment_counters(self):
        """
        Tests the increment_counters method to make sure they increment!

        """
        bagger = CarpetBag()
        assert bagger.request_count == 0
        assert bagger.request_total == 0
        bagger._increment_counters()
        assert bagger.request_count == 1
        assert bagger.request_total == 1
        bagger._increment_counters()
        assert bagger.request_count == 2
        assert bagger.request_total == 2

# End File carpetbag/tests/test_base_carpetbag.py
