"""Test CarpetBag methods which are under lying GET Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
from datetime import datetime
import os

import requests
import pytest

from carpetbag import CarpetBag, carpet_tools

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/vcr_cassettes')


SUCCESS_RETURN_CASSET = os.path.join(CASSET_DIR, "public_get_success.yaml")


class TestPublicGet(object):

    def test_get_successful(self):
        """
        Tests CarpetBag's main public method to make sure we're getting the responses we expect.

        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()
        api_url = carpet_tools.url_join(bagger.remote_service_api, "proxies/1")
        response = bagger.get(api_url)
        assert response.status_code == 200

    def test_get_user_agent(self):
        """
        Tests CarpetBag's main public method to make sure we're getting the responses we expect.

        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()
        bagger.user_agent = "Some-User-Agent"
        api_url = carpet_tools.url_join(bagger.remote_service_api, "proxies/1")
        response = bagger.get(api_url)
        assert response.status_code == 200
        assert bagger.send_user_agent == "Some-User-Agent"
        assert bagger.user_agent == "Some-User-Agent"

    def test_get_last_response_info(self):
        """
        Tests CarpetBag's main public method to make sure we're getting the responses we expect.

        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()
        bagger.user_agent = "Some-User-Agent"
        api_url = carpet_tools.url_join(bagger.remote_service_api, "proxies/1")
        assert not bagger.last_response
        response = bagger.get(api_url)
        assert response.status_code == 200
        # assert scraper.last_response.status_code == 200
        assert bagger.request_total == 1
        assert bagger.request_count == 1
        assert type(bagger.last_request_time) == datetime

    def test_get_host_unknown(self):
        """
        Tests CarpetBag's main public method to make sure we're rasing the requests.exceptions.Connetion error.

        """
        scraper = CarpetBag()
        scraper.user_agent = "Some-User-Agent"
        with pytest.raises(requests.exceptions.ConnectionError):
            scraper.get("http://0.0.0.0:90/api/symbol/")

# End File carpetbag/tests/test_public_get.py
