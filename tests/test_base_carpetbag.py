"""Test Base CarpetBag for the private methods of CarpetBag.

"""
from datetime import datetime, timedelta
import time
import os
import shutil

import arrow
import pytest
import requests

from carpetbag import CarpetBag
from carpetbag import carpet_tools as ct
from carpetbag import errors

from .data.response_data import GoogleDotComResponse

# UNIT_TEST_URL = os.environ.get("BAD_ACTOR_URL", "https//bas.bitgel.com")
UNIT_TEST_URL = "https//bas.bitgel.com/api"
UNIT_TEST_URL_BROKEN = "http://0.0.0.0:90/"
UNIT_TEST_AGENT = "CarpetBag v%s/ UnitTests" % CarpetBag.__version__


class TestBaseCarpetBag(object):

    def test___init__(self):
        """
        Tests that the module init has correct default values
        This test makes no outbound requests.

        """
        bagger = CarpetBag()
        assert bagger.headers == {}
        assert bagger.user_agent == "CarpetBag v%s" % bagger.__version__
        assert not bagger.random_user_agent
        assert bagger.mininum_wait_time == 0  # @todo: cover usage in unit test
        assert bagger.wait_and_retry_on_connection_error == 0  # @todo: cover usage in unit test
        assert bagger.retries_on_connection_failure == 5  # @todo: cover usage in unit test
        assert bagger.max_content_length == 200000000  # @todo: cover usage in unit test

        assert not bagger.username
        assert not bagger.password
        assert not bagger.auth_type
        assert bagger.change_identity_interval == 0  # @todo: build and test this functionality
        assert bagger.remote_service_api == UNIT_TEST_URL
        assert not bagger.outbound_ip
        assert bagger.request_count == 0
        assert bagger.request_total == 0
        assert not bagger.last_request_time
        assert not bagger.last_response
        assert bagger.manifest == []
        assert bagger.proxy == {}
        assert bagger.proxy_bag == []
        assert not bagger.random_proxy_bag
        assert bagger.send_user_agent == ""
        assert bagger.ssl_verify
        assert not bagger.send_usage_stats_val
        assert isinstance(bagger.usage_stats_api_key, str)
        assert not bagger.usage_stats_api_key
        assert isinstance(bagger.one_time_headers, list)
        assert not bagger.force_skip_ssl_verify

        assert bagger.paginatation_map == {
            "field_name_page": "page",
            "field_name_total_pages": "total_pages",
            "field_name_data": "objects",
        }

    def test___repr__(self):
        """
        Test CarpetBag's object representation.

        """
        bagger = CarpetBag()
        assert str(bagger) == "<CarpetBag>"
        bagger.proxy["http"] = "http://1.20.101.234:33085"
        assert str(bagger) == "<CarpetBag Proxy:http://1.20.101.234:33085>"
        bagger.proxy.pop("http")
        bagger.proxy["https"] = "https://1.20.101.234:33085"
        assert str(bagger) == "<CarpetBag Proxy:https://1.20.101.234:33085>"

    # def test__make_request(self):
    #     """
    #     Tests the BaseCarpetBag._make_request() method.
    #     @note: This test DOES make outbound web requests.

    #     """
    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify()
    #     request = bagger._make_request("GET", UNIT_TEST_URL)
    #     assert request
    #     assert request.text
    #     assert request.status_code == 200

    # def test__handle_sleep(self):
    #     """
    #     Tests the _handle_sleep() method to make sure sleep isnt used if mininum_wait_time is not set.
    #     @note: This test DOES make outbound web requests.

    #     """
    #     MINIMUM_WAIT = 10
    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify(force=True)
    #     bagger.mininum_wait_time = MINIMUM_WAIT

    #     # Make the first request
    #     start_1 = datetime.now()
    #     bagger.get(UNIT_TEST_URL)
    #     end_1 = datetime.now()
    #     run_time_1 = (end_1 - start_1).seconds
    #     assert run_time_1 < 5

    #     # Make the second request, to the same domain and check for a pause.
    #     start_2 = datetime.now()
    #     bagger._handle_sleep(UNIT_TEST_URL)
    #     end_2 = datetime.now()
    #     run_time_2 = (end_2 - start_2).seconds
    #     assert run_time_2 >= MINIMUM_WAIT - 1

    # def test__get_headers(self):
    #     """
    #     Tests that headers can be set by the CarpetBag application, and by the end-user.

    #     """
    #     bagger = CarpetBag()
    #     bagger.headers = {"Content-Type": "application/html"}
    #     bagger.user_agent = "Mozilla/5.0 (Windows NT 10.0)"
    #     set_headers = bagger._get_headers()
    #     assert set_headers["Content-Type"] == "application/html"
    #     assert set_headers["User-Agent"] == "Mozilla/5.0 (Windows NT 10.0)"

    # def test__validate_continents(self):
    #     """
    #     Tests the BaseCarpetBag._validate_continents() method to make sure we only are using valid contintent names.

    #     """
    #     bagger = CarpetBag()
    #     assert bagger._validate_continents(["North America"])
    #     assert bagger._validate_continents(["North America", "South America"])

    #     with pytest.raises(errors.InvalidContinent):
    #         bagger._validate_continents(["Nortf America"])

    # def test__set_user_agent(self):
    #     """
    #     Tests to make sure _set_user_agent will not override a manually set user_agent.

    #     """
    #     bagger = CarpetBag()
    #     bagger.user_agent = "My test user agent 1"
    #     bagger._set_user_agent()
    #     assert bagger.send_user_agent == "My test user agent 1"

    #     bagger.user_agent = "My test user agent 2"
    #     bagger._set_user_agent()
    #     assert bagger.send_user_agent == "My test user agent 2"

    # def test__fmt_request_args(self):
    #     """
    #     Tests BaseCarpetBag._fmt_request_args to make sure the dict is properly built.

    #     """
    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify()  # Test that "verify" is added to the args.
    #     bagger.use_random_public_proxy()  # Test that "proxy" is added to the args.

    #     request_args = bagger._fmt_request_args(
    #         "GET",
    #         {"Content-Type": "application/json"},
    #         UNIT_TEST_URL)

    #     assert isinstance(request_args, dict)
    #     assert request_args["method"] == "GET"
    #     assert request_args["url"] == UNIT_TEST_URL
    #     assert request_args["headers"] == {"Content-Type": "application/json"}
    #     assert request_args["verify"]
    #     assert (request_args["proxies"].get("http") or request_args["proxies"].get("https"))

    # def test__make(self):
    #     """
    #     Tests the _make() method of CarpetBag. This is one of the primary methods of CarpetBag, and could always use
    #     more tests!
    #     @note: This test DOES make outbound web requests.

    #     """
    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify()
    #     bagger._start_request_manifest("GET", UNIT_TEST_URL, {})
    #     response = bagger._make(
    #         method="GET",
    #         url=UNIT_TEST_URL,
    #         headers={"Content-Type": "application/html"},
    #         payload={},
    #         retry=0)
    #     bagger.manifest.append({})
    #     assert response
    #     assert response.status_code == 200
    #     response = bagger._make(
    #         method="GET",
    #         url=UNIT_TEST_URL,
    #         headers={"Content-Type": "application/html"},
    #         payload={},
    #         retry=0)
    #     assert response
    #     assert response.status_code == 200

    def test_make_internal(self):
        """
        Tests the BaseCarpetBagger()._make_internal() method to make sure we're communicating with the
        Bad-Actor.Services API correctly.
        @note: This test DOES make outbound web requests.

        """
        bagger = CarpetBag()
        response = bagger._make_internal("ip")
        assert str(response.json()["ip"])

        bagger.remote_service_api = UNIT_TEST_URL_BROKEN
        with pytest.raises(errors.NoRemoteServicesConnection):
            response = bagger._make_internal("ip")

    def test__internal_proxies_filter_continent_param(self):
        """
        Tests the BaseCarpetBagger()._internal_proxies_filter_continent_param() to make sure we're adding the continent
        filter correctly.

        """
        payload = {
            "continent": "Asia"
        }
        bagger = CarpetBag()
        _filter = bagger._internal_proxies_filter_continent_param(payload)
        assert _filter["name"] == "continent"
        assert _filter["op"] == "eq"
        assert _filter["val"] == "Asia"

    def test__internal_proxies_filter_last_test_param(self):
        """
        Tests the BaseCarpetBagger()._internal_proxies_filter_continent_param() to make sure we're adding the continent
        filter correctly.

        """
        bagger = CarpetBag()
        _filter = bagger._internal_proxies_filter_last_test_param({})
        weeks_ago_date = arrow.utcnow().datetime - timedelta(weeks=bagger.public_proxies_max_last_test_weeks + 1)

        assert _filter["name"] == "last_tested"
        assert _filter["op"] == ">"
        assert ct.json_to_date(_filter["val"]) > weeks_ago_date

    def test__handle_connection_error(self):
        """
        Tests the BaseCarpetBag._handle_connection_error() method, and tries to fetch data by retrying and updating
        proxies.
        @todo: Needs more test cases.

        """
        bagger = CarpetBag()
        with pytest.raises(requests.exceptions.ConnectionError):
            # bagger._start_request_manifest("GET", UNIT_TEST_URL_BROKEN, {})
            bagger.manifest.append({})
            bagger._handle_connection_error(
                method="GET",
                url=UNIT_TEST_URL_BROKEN,
                headers={},
                payload={},
                retry=0)

    def test__after_request(self):
        """
        Tests the CarepetBag._after_request method to make sure we're setting class vars as expected.
        @todo: This needs to have asserts waged, currently only checks to see if the method completely fails.

        """
        fake_start = int(round(time.time() * 1000)) - 5000
        bagger = CarpetBag()
        after_request = bagger._after_request(
            fake_start,
            UNIT_TEST_URL_BROKEN,
            GoogleDotComResponse())
        assert isinstance(after_request, int)

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

    def test__start_manifest(self):
        """
        Tests the BaseCarpetBag._start_request_manifest() to make sure it creates the record manifest.

        """
        bagger = CarpetBag()
        new_manifest = bagger._start_request_manifest("GET", UNIT_TEST_URL)
        assert isinstance(new_manifest, dict)
        assert new_manifest["method"] == "GET"
        assert new_manifest["url"] == UNIT_TEST_URL
        assert isinstance(new_manifest["date_start"], datetime)
        assert not new_manifest["date_end"]
        assert not new_manifest["response"]
        assert not new_manifest["errors"]
        assert len(bagger.manifest) == 1

    def test__end_manifest(self):
        """
        Tests the BaseCarpetBag()._end_manifest() method to make sure it caps off the end of the manifest and saves it
        to the class.

        """
        bagger = CarpetBag()
        current_manifest = {
            "method": "GET",
            "url": UNIT_TEST_URL,
            "payload_size ": 0,
            "date_start": arrow.utcnow(),
            "date_end": None,
            "roundtrip": None,
            "response": None,
            "retry": 0,
            "errors": []
        }
        bagger.manifest.insert(0, current_manifest)
        bagger._end_manifest("5", 1.54)
        assert isinstance(bagger.manifest, list)
        assert len(bagger.manifest) == 1
        assert bagger.manifest[0]["date_end"]
        assert bagger.manifest[0]["roundtrip"] == 1.54

    def test__cleanup_one_time_headers(self):
        """
        Tests the BaseCarpetBag()._cleanup_one_time_headers() to make sure it removes headers that are supposed to be
        destroy after a single use.

        """
        bagger = CarpetBag()
        bagger.one_time_headers = ["Test", "Headers"]
        bagger.headers = {
            "Test": "Some value",
            "Headers": "Some other value",
            "One that Stays": "Value"
        }
        bagger._cleanup_one_time_headers()
        assert "Test" not in bagger.headers
        assert "Headers" not in bagger.headers
        assert "One that Stays" in bagger.headers

    def test__determine_save_file_name(self):
        """
        Tests the BaseCarpetBag()._determine_save_file_name()
        @todo: Needs more test cases

        """
        bagger = CarpetBag()
        full_phile_name = bagger._determine_save_file_name(
            ct.url_join(UNIT_TEST_URL, "test/download/hacker-man.gif"),
            "image/gif",
            "/opt/carpetbag/tests/data")
        assert full_phile_name == "/opt/carpetbag/tests/data/hacker-man.gif"

        full_phile_name = bagger._determine_save_file_name(
            ct.url_join(UNIT_TEST_URL, "ip"),
            "application/json",
            "/opt/carpetbag/tests/data")
        assert full_phile_name == "/opt/carpetbag/tests/data/ip.json"

    def test__prep_destination(self):
        """
        Tests the BaseCarpetBag._prep_destination method to make sure we have dirs ready to go when needed to store
        files into.

        """
        bagger = CarpetBag()
        dirname, filename = os.path.split(os.path.abspath(__file__))
        new_dirs = os.path.join(dirname, "..", "one", "two")
        if os.path.exists(new_dirs):
            shutil.rmtree(new_dirs)

        # Check that we build the dir
        bagger._prep_destination(new_dirs)
        path_existance = os.path.isdir(new_dirs)
        assert path_existance

        # Remove the dir we must made.
        if os.path.exists(new_dirs):
            shutil.rmtree(os.path.join(dirname, "..", "one"))

# End File carpetbag/tests/test_base_carpetbag.py
