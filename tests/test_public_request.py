"""Test CarpetBag methods which are using any HTTP verb's Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
import os

import vcr

from carpetbag import CarpetBag

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data/vcr_cassettes")


class TestGet(object):

    def test_request_successful(self):
        """
        Tests CarpetBag's main public method, currently only for a GET Response

        """
        bagger = CarpetBag()
        bagger.use_skip_ssl_verify()
        success_url = bagger.url_join(bagger.remote_service_api, "/proxies")
        with vcr.use_cassette(os.path.join(CASSET_DIR, "request_successful.yaml")):
            response = bagger.request("GET", success_url)
            assert response.status_code == 200
            assert response.text

# End File carpetbag/tests/test_public_request.py
