"""Test Base Scrapy. Tests for the private methods of scrapy.

"""
import os

from scrapy import Scrapy

import vcr


CASSET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/vcr_cassettes')


class TestBaseScrapy(object):

    def test___init__(self):
        """
        Tests that the module init has correct default values.

        """
        s = Scrapy()
        assert s.proxies == {}
        assert s.headers == {}
        assert s.user_agent == ''
        assert s.skip_ssl_verify
        assert s.change_identity_interval == 0
        assert not s.outbound_ip
        assert s.request_attempts == {}
        assert s.request_count == 0
        assert s.request_total == 0
        assert not s.last_request_time
        assert not s.last_response
        assert s.send_user_agent == ''
        assert s.max_content_length == 200000000
        assert s.mininum_wait_time == 0
        assert s.wait_and_retry_on_connection_error == 0
        assert not s.username
        assert not s.password
        assert not s.auth_type
        assert not s.use_proxy_bag
        assert s.proxy_bag == []
        assert s.manifest == {}

    def test__make_request(self):
        scraper = Scrapy()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'test__make_request.yaml')):
            request = scraper._make_request('GET', 'http://www.google.com/news')
        assert request
        assert request.text
        assert request.status_code == 200

    def test__get_headers(self):
        """
        Tests that headers can be set by the scrapy application, and by the end-user.

        """
        s = Scrapy()
        s.headers = {'Content-Type': 'application/html'}
        s.user_agent = "Mozilla/5.0 (Windows NT 10.0)"
        set_headers = s._get_headers()
        assert set_headers['Content-Type'] == 'application/html'
        assert set_headers['User-Agent'] == "Mozilla/5.0 (Windows NT 10.0)"

    def test__setup_proxies(self):
        """
        Tests that proxies are defaulted to http and https if not specified.

        """
        s = Scrapy()
        assert not s.proxies
        s.proxies = {'http': 'localhost:8118'}
        s._setup_proxies()
        assert s.proxies['https'] == 'localhost:8118'
        assert s.proxies['http'] == 'localhost:8118'

    def test__set_user_agent_manual(self):
        """
        Tests to make sure _set_user_agent will not override a manually set user_agent.

        """
        s = Scrapy()
        s.user_agent = 'My test user agent'
        s._set_user_agent()
        assert s.send_user_agent == 'My test user agent'

        s.request_count = 2
        s.change_user_agent_interval = 2
        s._set_user_agent()
        assert s.send_user_agent == 'My test user agent'

    def test__increment_counters(self):
        """
        Tests the increment_counters method to make sure they increment!

        """
        s = Scrapy()
        assert s.request_count == 0
        assert s.request_total == 0
        s._increment_counters()
        assert s.request_count == 1
        assert s.request_total == 1
        s._increment_counters()
        assert s.request_count == 2
        assert s.request_total == 2

    def test__get_domain(self):
        """
        Tests the increment_counters method to make sure they increment!
        @todo: Fix the ip fetching portion of this domain.

        """
        scraper = Scrapy()
        assert scraper._get_domain('http://192.168.50.137:5000') == '192.168.50.137'
        assert scraper._get_domain('http://www.google.com') == 'google.com'
        assert scraper._get_domain('http://localhost') == 'localhost'
        # assert scraper._get_domain('http://192.168.50.137:5000') == '192.168.50.137'


# End File scrapy/tests/test_scrapy.py
