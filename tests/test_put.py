"""Test Scrapy methods which are under lying GET Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
import json
import os

import vcr

from scrapy import Scrapy

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/vcr_cassettes')

SCRAPE_BASE = 'http://192.168.50.137:5000/api/'


class TestPut(object):

    def test_post_one(self):
        """
        Tests Scrapy's main public method to make sure we're getting the responses we expect.

        """
        scraper = Scrapy()
        scraper.headers = {'Content-Type': 'application/json'}

        payload = {}
        payload['ts_updated'] = scraper.json_date()
        api_url = "http://www.bad-actor.services/api/symbols/1"
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'put_success.yaml')):
            response = scraper.put(
                api_url,
                payload=json.dumps(payload))
        assert response.status_code == 200

# End File scrapy/tests/test_put.py
