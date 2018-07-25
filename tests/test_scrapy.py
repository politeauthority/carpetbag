"""Test Scrapy
Run by using "pytest ." in the project root.

"""

from scrapy.scrapy import Scrapy
from scrapy import user_agent


class TestScrapy(object):

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
        Tests to make sure _set_user_agent will not override a manually set user_agent.

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
        s._increment_counters()
        assert s.request_count == 1
        assert s.request_total == 1
        s._increment_counters()
        assert s.request_count == 2
        assert s.request_total == 2
