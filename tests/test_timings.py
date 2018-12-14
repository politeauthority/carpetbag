"""Test Scrapy methods which are under lying GET Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
from datetime import datetime
import os

import requests
import pytest
import vcr

from carpetbag import CarpetBag

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data/vcr_cassettes")


class TestTimings(object):

    def test_minimum_wait(self):
        """
        Tests Scrapy"s main public method to make sure we"re waiting when the minim

        """
        start = datetime.now()

        scraper = CarpetBag()
        scraper.mininum_wait_time = 3
        with vcr.use_cassette(os.path.join(CASSET_DIR, "timings_minimum_wait.yaml")):
            scraper.get("http://www.bad-actor.services/api/symbols/1")
            scraper.get("http://www.bad-actor.services/api/symbols/2")
            scraper.get("http://www.bad-actor.services/api/something-wont-work/1")

        end = datetime.now()
        run_time = (end - start).seconds
        assert run_time >= scraper.mininum_wait_time * 2
        assert scraper.mininum_wait_time == 3

    def test_retry_on_bad_connection(self):
        """
        Tests that when the wait_and_retry_on_connection_error has a value, that we do the retries and wait the at
        least the specified ammount of time between requests.

        """
        start = datetime.now()

        scraper = CarpetBag()
        scraper.wait_and_retry_on_connection_error = 3
        with vcr.use_cassette(os.path.join(CASSET_DIR, "timings_retry_bad_conn.yaml")):
            with pytest.raises(requests.exceptions.ConnectionError):
                scraper.get("http://0.0.0.0:90/api/symbols/1")

        end = datetime.now()
        run_time = (end - start).seconds
        assert run_time >= scraper.wait_and_retry_on_connection_error * 4
        assert scraper.request_total == 1
        assert scraper.request_count == 1

# End File carpetbag/tests/test_timings.py
