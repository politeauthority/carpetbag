"""Test Scrapy methods which are under lying GET Request/Responses
This uses the vcr module to mimick responses to http requests. This tests the module as a whole.

"""
from datetime import datetime
import os

import requests
import pytest
import vcr

from scrapy import Scrapy

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/vcr_cassettes')


class TestGet(object):

    def test_get_successful(self):
        """
        Tests Scrapy's main public method to make sure we're getting the responses we expect.

        """
        scraper = Scrapy()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'bad_actor_get.yaml')):
            response = scraper.get('http://www.bad-actor.services/api/symbols/1')
            assert response.status_code == 200

    def test_get_user_agent(self):
        """
        Tests Scrapy's main public method to make sure we're getting the responses we expect.

        """
        scraper = Scrapy()
        scraper.user_agent = 'Some-User-Agent'
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'bad_actor_get_user_agent.yaml')):
            response = scraper.get('http://www.bad-actor.services/api/symbols/1')
            assert response.status_code == 200
            assert scraper.send_user_agent == 'Some-User-Agent'
            assert scraper.user_agent == 'Some-User-Agent'

    def test_get_last_response_info(self):
        """
        Tests Scrapy's main public method to make sure we're getting the responses we expect.

        """
        scraper = Scrapy()
        # request_attempts = {
        #     'services': {
        #         'urls': {
        #             'http://www.bad-actor.services/api/symbols/1': {
        #                 'count': 1
        #             }
        #         },
        #         'total_requests': 1
        #     }
        # }
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'bad_actor_get.yaml')):
            response = scraper.get('http://www.bad-actor.services/api/symbols/1')
            assert response.status_code == 200
            assert scraper.last_response.status_code == 200
            assert scraper.request_total == 1
            assert scraper.request_count == 1
            # assert scraper.request_attempts == request_attempts
            assert type(scraper.last_request_time) == datetime

    def test_get_404_response(self):
        """
        Tests Scrapy's main public method to make sure we're getting the responses we expect.

        """
        scraper = Scrapy()
        scraper.user_agent = 'Some-User-Agent'
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'bad_actor_get_404.yaml')):
            response = scraper.get('http://www.bad-actor.services/api/symbol/1')
            assert response.status_code == 404

    def test_get_host_unknown(self):
        """
        Tests Scrapy's main public method to make sure we're rasing the requests.exceptions.Connetion error.

        """
        scraper = Scrapy()
        scraper.user_agent = 'Some-User-Agent'
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'bad_actor_get_unknown.yaml')):
            with pytest.raises(requests.exceptions.ConnectionError):
                scraper.get('http://www.12345151dfsdf.com/api/symbol/1')

    def test_search_one(self):
        """
        Tests Scrapy's search, which runs a search on DuckDuckGo and parses the response.

        """
        scraper = Scrapy()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'search_one.yaml')):
            response = scraper.search('learn python')
            assert response['results'][0]['title'] == 'Learn Python | Udemy.com\nAd'

    def test_check_tor_fail(self):
        """
        Tests the method Scrapy().check_tor(), this test mocks out a failure of connecting to tor.

        """
        scraper = Scrapy()
        tor = scraper.check_tor()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'check_tor_fail.yaml')):
            assert tor == 'Sorry. You are not using Tor.'

    def test_get_outbound_ip(self):
        """
        Tests the Scrapy().get_outbound_ip method to make sure we get and parse the outbound IP correctly.

        """
        scraper = Scrapy()
        ip = scraper.get_outbound_ip()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'get_outbound_ip.yaml')):
            assert ip == '73.203.37.237'

# End File scrapy/tests/test_get.py
