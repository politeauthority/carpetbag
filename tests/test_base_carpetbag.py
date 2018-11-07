"""Test Base CarpetBag. Tests for the private methods of CarpetBag.

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
        scraper = CarpetBag()
        assert s.proxy == {}
        assert s.headers == {}
        assert s.user_agent == "CarpetBag v.001"
        assert s.ssl_verify
        assert s.change_identity_interval == 0
        assert not s.outbound_ip
        assert s.request_attempts == {}
        assert s.request_count == 0
        assert s.request_total == 0
        assert not s.last_request_time
        assert not s.last_response
        assert s.send_user_agent == ""
        assert s.max_content_length == 200000000
        assert s.mininum_wait_time == 0
        assert s.wait_and_retry_on_connection_error == 0
        assert not s.username
        assert not s.password
        assert not s.auth_type
        assert not s.random_proxy_bag
        assert s.proxy_bag == []
        assert s.manifest == {}

    def test__make_request(self):
        scraper = CarpetBag()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "test__make_request.yaml")):
            request = scraper._make_request("GET", "http://www.google.com/news")
        assert request
        assert request.text
        assert request.status_code == 200

    def test__handle_sleep_1(self):
        """
        Tests the _handle_sleep() method to make sure sleep isnt used if mininum_wait_time is not set.

        """
        scraper = CarpetBag()
        start_1 = datetime.now()
        scraper._handle_sleep("https://www.google.com/")
        end_1 = datetime.now()
        run_time_1 = (end_1 - start_1).seconds
        assert run_time_1 < 3

        scraper = CarpetBag()
        start_2 = datetime.now()
        scraper._handle_sleep("https://www.google.com/")
        end_2 = datetime.now()
        run_time_2 = (end_2 - start_2).seconds
        assert run_time_2 < 3

    def test__handle_sleep_2(self):
        """
        Tests the _handle_sleep() method to make sure sleep is used on the second request, then dropped for the first
        request of a new domain.

        """
        scraper = CarpetBag()
        scraper.mininum_wait_time = 5

        start_1 = datetime.now()
        scraper._handle_sleep("https://www.google.com/")
        end_1 = datetime.now()
        run_time_1 = (end_1 - start_1).seconds
        assert run_time_1 < 3

        start_2 = datetime.now()
        scraper.last_request_time = start_1
        scraper.last_response = GoogleDotComResponse()
        scraper._handle_sleep("https://www.google.com/")
        end_2 = datetime.now()
        run_time_2 = (end_2 - start_2).seconds
        assert run_time_2 >= 4

        start_3 = datetime.now()
        scraper.last_request_time = start_1
        scraper._handle_sleep("https://www.example.com/")
        end_3 = datetime.now()
        run_time_3 = (end_3 - start_3).seconds
        assert run_time_3 < 3

    def test__get_domain(self):
        """
        Tests the BaseCarpetBag._get_domain method to see if it properly picks the domain from a url.

        """
        scraper = CarpetBag()
        assert scraper._get_domain("http://192.168.50.137:5000") == "192.168.50.137"
        assert scraper._get_domain("http://www.google.com") == "google.com"
        assert scraper._get_domain("http://localhost") == "localhost"
        assert scraper._get_domain("http://192.168.1.19:5010") == "192.168.1.19"

    def test__get_headers(self):
        """
        Tests that headers can be set by the CarpetBag application, and by the end-user.

        """
        scraper = CarpetBag()
        scraper.headers = {"Content-Type": "application/html"}
        scraper.user_agent = "Mozilla/5.0 (Windows NT 10.0)"
        set_headers = s._get_headers()
        assert set_headers["Content-Type"] == "application/html"
        assert set_headers["User-Agent"] == "Mozilla/5.0 (Windows NT 10.0)"

    def test__setup_proxy(self):
        """
        Tests that proxies are defaulted to http and https if not specified.

        """
        scraper = CarpetBag()
        assert not s.proxy
        scraper.proxy = {"http": "localhost:8118"}
        scraper._setup_proxies()
        assert scraper.proxy["https"] == "localhost:8118"
        assert scraper.proxy["http"] == "localhost:8118"

    def test__filter_public_proxies(self):
        """
        Tests the filtering of the public proxies CarpetBag gathers.
        First assertion makes sure we filter SSL only proxies
        Second assert makes sure we grab proxies only from North America
        Third assertion checks that the first proxies is from North Amercia
        Fourth assertion checks that we order South America after North America

        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_data = open(os.path.join(dir_path, 'data/default_proxy_bag.json')).read()
        test_proxies = json.loads(json_data)
        scraper = CarpetBag()
        assert isinstance(scraper._filter_public_proxies(test_proxies, [], False), list)

        # Check that we get only SSL supporting proxies
        filtered_proxies = scraper._filter_public_proxies(test_proxies, continents=[], ssl_only=True)
        for proxy in filtered_proxies:
            assert proxy['ssl']

        # Check that we can grab proxies based on a single contintent
        filtered_proxies = scraper._filter_public_proxies(test_proxies, continents=["North America"])
        for proxy in filtered_proxies:
            assert proxy['continent'] == "North America"

        # Check that we grab proxies from multiple continents, ordered appropriately.
        filtered_proxies = scraper._filter_public_proxies(test_proxies, continents=["North America", 'South America'])
        assert filtered_proxies[0]['continent'] == "North America"
        assert filtered_proxies[len(filtered_proxies) - 1]['continent'] == "South America"

        with pytest.raises(errors.InvalidContinent):
            filtered_proxies = scraper._filter_public_proxies(test_proxies, continents=["Nortf America"])

    def test__set_user_agent_manual(self):
        """
        Tests to make sure _set_user_agent will not override a manually set user_agent.

        """
        scraper = CarpetBag()
        scraper.user_agent = "My test user agent"
        scraper._set_user_agent()
        assert s.send_user_agent == "My test user agent"

        scraper.request_count = 2
        scraper.change_user_agent_interval = 2
        scraper._set_user_agent()
        assert scraper.send_user_agent == "My test user agent"

    def test__make_1(self):
        """
        Tests the _make() method of CarpetBag. This is one of the primary methods of CarpetBag, and could always use
        more tests!

        """
        s = CarpetBag()
        with vcr.use_cassette(os.path.join(CASSET_DIR, "test__make_1.yaml")):
            response = s._make(
                method="GET",
                url="http://www.google.com",
                headers={"Content-Type": "application/html"},
                payload={},
                retry=0)
            assert response
            assert response.status_code == 200
            response = s._make(
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
        scraper = CarpetBag()
        scraper._after_request(fake_start, "https://www.google.com", GoogleDotComResponse())

    def test__increment_counters(self):
        """
        Tests the increment_counters method to make sure they increment!

        """
        s = CarpetBag()
        assert s.request_count == 0
        assert s.request_total == 0
        s._increment_counters()
        assert s.request_count == 1
        assert s.request_total == 1
        s._increment_counters()
        assert s.request_count == 2
        assert s.request_total == 2

# End File CarpetBag/tests/test_base_carpetbag.py
