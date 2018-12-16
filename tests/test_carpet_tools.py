"""Tests Carpet Tools

"""
from datetime import datetime

from carpetbag import carpet_tools


class TestCarpetTools(object):


    def test_url_join(self):
        """
        Tests the url_join method. This is just an alias of url_concat.
        We check to make sure we're not adding any extra slashes or making weird urls.

        """
        assert carpet_tools.url_join("www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert carpet_tools.url_join("https://www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert carpet_tools.url_join("https://www.bad-actor.services", "/api") == "https://www.bad-actor.services/api"
        assert carpet_tools.url_join("https://www.bad-actor.services", "/") == "https://www.bad-actor.services/"
        assert carpet_tools.url_join("https://www.bad-actor.services/", "/") == "https://www.bad-actor.services/"

    def test_url_concat(self):
        """
        Tests the url_concat method, to make sure we're not adding any extra slashes or making weird urls.

        """
        assert carpet_tools.url_join("www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert carpet_tools.url_concat("https://www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert carpet_tools.url_concat("https://www.bad-actor.services", "/api") == "https://www.bad-actor.services/api"
        assert carpet_tools.url_concat("https://www.bad-actor.services", "/") == "https://www.bad-actor.services/"
        assert carpet_tools.url_concat("https://www.bad-actor.services/", "/") == "https://www.bad-actor.services/"

    def test_json_date(self):
        """
        Tests the JSON date method to try and convert the information to JSON friendly output.

        """
        now = datetime.now()
        the_date = datetime(2018, 10, 13, 12, 12, 12)
        assert carpet_tools.json_date(the_date) == "2018-10-13 12:12:12"
        assert isinstance(carpet_tools.json_date(), str)
        assert carpet_tools.json_date()[:4] == str(now.year)

    def test_remove_protocol(self):
        """
        Tests the carpet_tools.remove_protocol() method to ensure it properly takes off http:// and https:// from a
        string. Keep in mind this only removes http:// and https:// protocals.

        """
        assert carpet_tools.remove_protocol("http://google.com") == "google.com"
        assert carpet_tools.remove_protocol("https://google.com") == "google.com"
        assert carpet_tools.remove_protocol("http://www.google.com") == "www.google.com"

    def test_get_domain(self):
        """
        Tests the BaseCarpetBag._get_domain method to see if it properly picks the domain from a url.

        """
        assert carpet_tools.get_domain("http://192.168.50.137:5000") == "192.168.50.137"
        assert carpet_tools.get_domain("http://www.google.com") == "google.com"
        assert carpet_tools.get_domain("http://localhost") == "localhost"
        assert carpet_tools.get_domain("http://192.168.1.19:5010") == "192.168.1.19"
