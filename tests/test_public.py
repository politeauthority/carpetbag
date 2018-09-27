"""Test Scrapy's public methods that are not the basic HTTP verbs.

"""
from datetime import datetime
import os

import vcr

from scrapy import Scrapy
from scrapy import user_agent

CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/vcr_cassettes')


class TestPublic(object):

    def test_json_date(self):
        """
        Tests the JSON date method to try and convert the information to JSON friendly output.

        """
        now = datetime.now()
        the_date = datetime(2018, 10, 13, 12, 12, 12)
        assert Scrapy.json_date(the_date) == '2018-10-13 12:12:12'
        assert isinstance(Scrapy.json_date(), str)
        assert Scrapy.json_date()[:4] == str(now.year)

    def test_url_concat(self):
        """
        Tests the url_concat method, to make sure we're not adding any extra slashes or making weird urls.

        """
        assert Scrapy.url_concat('http://www.google.com', 'news') == 'http://www.google.com/news'
        assert Scrapy.url_concat('http://www.google.com', '/news') == 'http://www.google.com/news'
        assert Scrapy.url_concat('http://www.google.com/', '/') == 'http://www.google.com/'
        assert Scrapy.url_concat('http://www.google.com', '/') == 'http://www.google.com/'

    def test_random_user_agent(self):
        """
        Tests Scrapy's main public method to make sure we're getting the responses we expect.

        """
        scraper = Scrapy()
        assert not scraper.user_agent
        scraper.random_user_agent()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'public_random_user_agent.yaml')):
            scraper.get('http://www.bad-actor.services')
        assert scraper.user_agent in user_agent.get_flattened_uas()

    def test_check_tor_fail(self):
        """
        Tests the method Scrapy().check_tor(), this test mocks out a failure of connecting to tor.

        """
        scraper = Scrapy()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'public_tor_fail.yaml')):
            tor = scraper.check_tor()
            assert not tor

    def test_get_outbound_ip(self):
        """
        Tests the Scrapy().get_outbound_ip method to make sure we get and parse the outbound IP correctly.

        """
        scraper = Scrapy()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'public_outbound_ip.yaml')):
            ip = scraper.get_outbound_ip()
            assert ip == '73.203.37.237'

# End File scrapy/tests/test_public.py
