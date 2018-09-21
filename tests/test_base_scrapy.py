"""Test Scrapy
Run by using "pytest ." in the project root.

"""
from datetime import datetime
import os

from scrapy import Scrapy
from scrapy import user_agent

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
        assert s.change_user_agent_interval == 10
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

    def test_json_date(self):
        """
        Tests the JSON date method to try and convert the information to JSON friendly output.

        """
        the_date = datetime(2018, 10, 13, 12, 12, 12)
        assert Scrapy.json_date(the_date) == '2018-10-13 12:12:12'
        assert isinstance(Scrapy.json_date(), str)

    def test_url_concat(self):
        """
        Tests the url_concat method, to make sure we're not adding any extra slashes or making weird urls.

        """
        assert Scrapy.url_concat('www.google.com', 'news') == 'www.google.com/news'
        assert Scrapy.url_concat('www.google.com', '/news') == 'www.google.com/news'

    def test__make_request(self):
        scraper = Scrapy()
        with vcr.use_cassette(os.path.join(CASSET_DIR, 'test__make_request.yaml')):
            scraper._make_request('GET', 'http://www.google.com/news')

    # def test__request_attempts(self):
    #     """
    #     Tests that the request_attempts method is adding values to manifest var.

    #     """
    #     s = Scrapy()
    #     ret = s._request_attempts('http://google.com/news')
    #     assert 'http://google.com/news' in ret['urls']
    #     assert ret['urls']['http://google.com/news']['count'] == 1

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
        s.proxies = {'http': 'localhost'}
        s._setup_proxies()
        assert s.proxies['https'] == 'localhost'
        assert s.proxies['http'] == 'localhost'

    def test__set_user_agent_auto(self):
        """
        Tests to make sure user agents are auto assigned, and rotated when the interval is reached.

        """
        s = Scrapy()
        s._set_user_agent()
        all_user_agents = user_agent.get_flattened_uas()
        first_assigned_user_agent = s.send_user_agent
        assert s.send_user_agent in all_user_agents
        s.request_count = 2
        s.change_user_agent_interval = 2
        s._set_user_agent()
        assert s.send_user_agent
        assert s.send_user_agent != first_assigned_user_agent

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
        assert scraper._get_domain('http://www.google.com') == 'google.com'
        assert scraper._get_domain('http://localhost') == 'localhost'
        # assert scraper._get_domain('http://192.168.50.137:5000') == '192.168.50.137'


# End File scrapy/tests/test_scrapy.py
