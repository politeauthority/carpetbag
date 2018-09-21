"""Test Scrapy methods which are under lying GET Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
from datetime import datetime
import os

import requests
import pytest
import vcr

from scrapy.scrapy import Scrapy
from scrapy import user_agent

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/vcr_cassettes')


class TestPost(object):

    def test_post_one(self):
        """
        Tests Scrapy's main public method to make sure we're getting the responses we expect.

        """
        scraper = Scrapy()
        scraper.headers = {'Content-Type': 'application/json'}

        payload = {}
        payload['symbol'] = 'MSFT'
        payload['exchange'] = 'nasdaq'
        payload['name'] = 'Microsoft'
        payload['sector'] = 'Technology'
        payload['industry'] = 'Technology Industry'

        api_url = "http://192.168.7.78:5000/api/symbols"

        response = scraper.post(
            api_url,
            payload=payload)

        assert response.status_code == 200

if __name__ == '__main__':
    scraper = Scrapy()
    scraper.headers = {'Content-Type': 'application/json'}

    payload = {}
    payload['symbol'] = 'MSFT'
    payload['exchange'] = 'nasdaq'
    payload['name'] = 'Microsoft'
    payload['sector'] = 'Technology'
    payload['industry'] = 'Technology Industry'

    api_url = "http://192.168.7.78:5000/api/symbols"

    response = scraper.post(
        api_url,
        payload=payload)

# End File scrapy/tests/test_post.py
