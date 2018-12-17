"""Tests Carpet Tools

"""
from datetime import datetime

from carpetbag import carpet_tools as ct


class TestCarpetTools(object):

    def test_url_join(self):
        """
        Tests the url_join method. This is just an alias of url_concat.
        We check to make sure we're not adding any extra slashes or making weird urls.

        """
        assert ct.url_join("www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert ct.url_join("https://www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert ct.url_join("https://www.bad-actor.services", "/api") == "https://www.bad-actor.services/api"
        assert ct.url_join("https://www.bad-actor.services", "/") == "https://www.bad-actor.services/"
        assert ct.url_join("https://www.bad-actor.services/", "/") == "https://www.bad-actor.services/"

    def test_url_concat(self):
        """
        Tests the carpet_tools.url_concat() method, to make sure we're not adding any extra slashes or making weird
        urls.

        """
        assert ct.url_join("www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert ct.url_concat("https://www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert ct.url_concat("https://www.bad-actor.services", "/api") == "https://www.bad-actor.services/api"
        assert ct.url_concat("https://www.bad-actor.services", "/") == "https://www.bad-actor.services/"
        assert ct.url_concat("https://www.bad-actor.services/", "/") == "https://www.bad-actor.services/"

    def test_url_disect(self):
        """
        Tests the carpet_tools.url_disect() method to make sure it pulls urls appart correctly.

        """
        url_pieces = ct.url_disect("https://www.bad-actor.services/some/url-thats-long?debug=True")

        assert url_pieces
        assert isinstance(url_pieces, dict)
        assert "protocol" in url_pieces
        assert "domain" in url_pieces
        assert "sub_domains" in url_pieces
        assert "tld" in url_pieces
        assert "url" in url_pieces
        assert "last" in url_pieces
        assert "params" in url_pieces

        assert url_pieces["protocol"] == "https"
        assert url_pieces["domain"] == "bad-actor.services"
        assert "www" in url_pieces["sub_domains"]

        assert url_pieces["tld"] == "services"
        assert url_pieces["url"] == "www.bad-actor.services/some/url-thats-long"
        assert url_pieces["last"] == "url-thats-long"
        assert isinstance(url_pieces["params"], dict)
        assert url_pieces["params"]["debug"] == "True"

    def test_json_date(self):
        """
        Tests the JSON date method to try and convert the information to JSON friendly output.

        """
        now = datetime.now()
        the_date = datetime(2018, 10, 13, 12, 12, 12)
        assert ct.json_date(the_date) == "2018-10-13 12:12:12"
        assert isinstance(ct.json_date(), str)
        assert ct.json_date()[:4] == str(now.year)

    def test_remove_protocol(self):
        """
        Tests the carpet_tools.remove_protocol() method to ensure it properly takes off http:// and https:// from a
        string. Keep in mind this only removes http:// and https:// protocals.

        """
        assert ct.remove_protocol("http://google.com") == "google.com"
        assert ct.remove_protocol("https://google.com") == "google.com"
        assert ct.remove_protocol("http://www.google.com") == "www.google.com"

    def test_get_domain(self):
        """
        Tests the BaseCarpetBag._get_domain method to see if it properly picks the domain from a url.

        """
        assert ct.get_domain("http://www.google.com") == "google.com"
        assert ct.get_domain("http://localhost") == "localhost"
        assert ct.get_domain("http://192.168.1.19:5010") == "192.168.1.19"
