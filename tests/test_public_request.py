"""Test Scrapy methods which are under lying GET Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
import os

import vcr

from scrapy import Scrapy

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/vcr_cassettes')


class TestGet(object):

    def test_request_successful(self):
        """
        Tests Scrapy's main public method, currently only for a GET Response

        """
        scraper = Scrapy()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'request_successful.yaml')):
            response = scraper.request('GET', 'http://www.bad-actor.services/api/symbols/1')
            assert response.status_code == 200
            assert response.text

# End File scrapy/tests/test_request.py
