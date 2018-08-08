"""Test Scrapy
Run by using "pytest ." in the project root.

"""
from scrapy.scrapy import Scrapy
from scrapy import user_agent


class TestScrapy(object):

    def test___init__(self):
        """
        Tests that the module init has correct default values.

        """
        s = Scrapy()
        s.proxies = {}
        s.headers = {}
        s.user_agent = ''
        s.skip_ssl_verify = True
        s.change_user_agent_interval = 10
        s.outbound_ip = None
        s.request_attempts = {}
        s.request_count = 0
        s.request_total = 0
        s.last_request_time = None
        s.last_response = None
        s.send_user_agent = ''

    def test_url_concat(self):
        assert Scrapy.url_concat('www.google.com', 'news') == 'www.google.com/news'
        assert Scrapy.url_concat('www.google.com', '/news') == 'www.google.com/news'

    def test__request_attempts(self):
        """
        Tests that the request_attempts method is adding values to manifest var.

        """
        s = Scrapy()
        ret = s._request_attempts('http://google.com/news')
        assert 'http://google.com/news' in ret['urls']
        assert ret['urls']['http://google.com/news']['count'] == 1

    def test__set_headers(self):
        """
        Tests that headers can be set by the scrapy application, and by the end-user.

        """
        s = Scrapy()
        set_headers = s._set_headers({}, {'Content-Type': 'application/json'})
        assert set_headers['Content-Type'] == 'application/json'

        s = Scrapy()
        s.headers = {'Content-Type': 'application/html'}
        set_headers = s._set_headers({}, {})
        assert set_headers['Content-Type'] == 'application/html'

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
