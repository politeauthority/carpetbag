"""Test Base CarpetBag for the private methods of CarpetBag.

"""
from datetime import datetime
import time
import os
import shutil

import arrow
import pytest
import requests
# import vcr

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
        assert bagger.headers == {}
        assert bagger.user_agent == "CarpetBag v%s" % bagger.__version__
        assert not bagger.random_user_agent
        assert bagger.mininum_wait_time == 0
        assert bagger.wait_and_retry_on_connection_error == 0
        assert bagger.retries_on_connection_failure == 5
        assert bagger.max_content_length == 200000000

        assert not bagger.username
        assert not bagger.password
        assert not bagger.auth_type
        assert bagger.change_identity_interval == 0
        assert bagger.remote_service_api == "https://www.bad-actor.services/api"
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

    def test__make_request(self):
        """
        Tests the BaseCarpetBag._make_request() method.

        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()
        # with vcr.use_cassette(os.path.join(CASSET_DIR, "google.com.yaml")):
        request = bagger._make_request("GET", "https://www.bad-actor.services/")
        assert request
        assert request.text
        assert request.status_code == 200

    def test__handle_sleep(self):
        """
        Tests the _handle_sleep() method to make sure sleep isnt used if mininum_wait_time is not set.

        """
        MINIMUM_WAIT = 10
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()
        bagger.mininum_wait_time = MINIMUM_WAIT

        # Make the first request
        start_1 = datetime.now()
        bagger.get("https://www.bad-actor.services/")
        end_1 = datetime.now()
        run_time_1 = (end_1 - start_1).seconds
        assert run_time_1 < 5

        # Make the second request, to the same domain and check for a pause.
        start_2 = datetime.now()
        bagger._handle_sleep("https://www.bad-actor.services/")
        end_2 = datetime.now()
        run_time_2 = (end_2 - start_2).seconds
        assert run_time_2 >= MINIMUM_WAIT - 1

    def test__get_headers(self):
        """
        Tests that headers can be set by the CarpetBag application, and by the end-user.

        """
        scraper = CarpetBag()
        scraper.headers = {"Content-Type": "application/html"}
        scraper.user_agent = "Mozilla/5.0 (Windows NT 10.0)"
        set_headers = scraper._get_headers()
        assert set_headers["Content-Type"] == "application/html"
        assert set_headers["User-Agent"] == "Mozilla/5.0 (Windows NT 10.0)"

    def test__validate_continents(self):
        """
        Tests the BaseCarpetBag._validate_continents() method to make sure we only are using valid contintent names.

        """
        bagger = CarpetBag()
        assert bagger._validate_continents(["North America"])
        assert bagger._validate_continents(["North America", "South America"])

        with pytest.raises(errors.InvalidContinent):
            bagger._validate_continents(["Nortf America"])

    def test__set_user_agent(self):
        """
        Tests to make sure _set_user_agent will not override a manually set user_agent.

        """
        bagger = CarpetBag()
        bagger.user_agent = "My test user agent 1"
        bagger._set_user_agent()
        assert bagger.send_user_agent == "My test user agent 1"

        bagger.user_agent = "My test user agent 2"
        bagger._set_user_agent()
        assert bagger.send_user_agent == "My test user agent 2"

    def test__fmt_request_args(self):
        """
        Tests BaseCarpetBag._fmt_request_args to make sure the dict is properly built.

        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()

        request_args = bagger._fmt_request_args(
            "GET",
            {"Content-Type": "application/json"},
            "https://bad-actor.services")

        assert isinstance(request_args, dict)
        assert request_args["method"] == "GET"
        assert request_args["url"] == "https://bad-actor.services"
        assert request_args["headers"] == {"Content-Type": "application/json"}
        assert request_args["verify"]

    def test__make(self):
        """
        Tests the _make() method of CarpetBag. This is one of the primary methods of CarpetBag, and could always use
        more tests!

        """
        bagger = CarpetBag()
        # with vcr.use_cassette(os.path.join(CASSET_DIR, "test__make_1.yaml")):
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

    def test_make_internal(self):
        """
        Tests the BaseCarpetBagger._make_internal() method to make sure we're communicating with the bad-actor.services
        API correctly.

        """
        bagger = CarpetBag()
        response = bagger._make_internal("ip")
        assert str(response["ip"])

        # @todo: Need to capture the NoRemoteServicesConnection on a bad url.
        bagger.remote_service_api = 'http://0.0.0.0:90/api'
        with pytest.raises(errors.NoRemoteServicesConnection):
            response = bagger._make_internal('ip')

    def test__handle_connection_error(self):
        """
        Tests the BaseCarpetBag._handle_connection_error() method, and tries to fetch data by retrying and updating
        proxies.
        @todo: Needs more test cases.

        """
        bagger = CarpetBag()
        with pytest.raises(requests.exceptions.ConnectionError):
            bagger._handle_connection_error(
                method="GET",
                url="https://0.0.0.0:90/",
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
        assert isinstance(bagger._after_request(fake_start, "https://www.google.com", GoogleDotComResponse()), int)

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
        Tests the BaseCarpetBag._start_new_manifest() to make sure it creates the record manifest.

        """
        bagger = CarpetBag()
        new_manifest = bagger._start_new_manifest("GET", "https://www.bad-actor.services")
        assert isinstance(new_manifest, dict)
        assert new_manifest["method"] == "GET"
        assert new_manifest["url"] == "https://www.bad-actor.services"
        # assert isinstance(new_manifest["date_start"], arrow)
        assert not new_manifest["date_end"]
        assert not new_manifest["response"]
        assert len(bagger.manifest) == 1

    def test__end_manifest(self):
        """
        Tests the BaseCarpetBag._end_manifest() method to make sure it caps off the end of the manifest and saves it to
        the class.

        """
        bagger = CarpetBag()
        current_manifest = {
            "method": "GET",
            "url": "https://www.bad-actor.services/",
            "payload_size ": 0,
            "date_start": arrow.utcnow(),
            "date_end": None,
            "roundtrip": None,
            "response": None,
            "retry": 0,
            "errors": []
        }
        bagger.manifest.insert(0, current_manifest)
        bagger._end_manifest('5', 1.54)
        assert isinstance(bagger.manifest, list)
        assert len(bagger.manifest) == 1
        assert bagger.manifest[0]["date_end"]
        assert bagger.manifest[0]["roundtrip"] == 1.54

    def test_prep_destination(self):
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
