"""Test Scrapy methods which are under lying GET Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
from datetime import datetime

import requests
import pytest

from carpetbag import CarpetBag


class TestTimings(object):

    # def test_minimum_wait(self):
    #     """
    #     Tests CarpetBag's main public method to make sure we"re waiting when the minim

    #     """
    #     start = datetime.now()

    #     bagger = CarpetBag()
    #     bagger.use_skip_ssl_verify()

    #     bagger.mininum_wait_time = 3
    #     # with vcr.use_cassette(os.path.join(CASSET_DIR, "timings_minimum_wait.yaml")):
    #     bagger.get(bagger.url_join(bagger.remote_service_api, "test404/1"))
    #     bagger.get(bagger.url_join(bagger.remote_service_api, "test404/2"))
    #     bagger.get(bagger.url_join(bagger.remote_service_api, "test404/3"))

    #     end = datetime.now()
    #     run_time = (end - start).seconds
    #     run_min_wait = int(bagger.mininum_wait_time * 2)
    #     assert run_time >= run_min_wait
    #     assert bagger.mininum_wait_time == 3

    def test_retry_on_bad_connection(self):
        """
        Tests that when the wait_and_retry_on_connection_error has a value, that we do the retries and wait the at
        least the specified ammount of time between requests.

        """
        start = datetime.now()

        bagger = CarpetBag()
        bagger.wait_and_retry_on_connection_error = 3
        with pytest.raises(requests.exceptions.ConnectionError):
            bagger.get("http://0.0.0.0:90/api/symbols/1")

        end = datetime.now()
        run_time = (end - start).seconds
        assert run_time >= bagger.wait_and_retry_on_connection_error * 4
        assert bagger.request_total == 1
        assert bagger.request_count == 1

# End File carpetbag/tests/test_timings.py
