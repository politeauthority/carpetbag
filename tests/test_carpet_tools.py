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
        assert ct.url_join("www.bad-actor.services", "api") == "http://www.bad-actor.services/api"
        assert ct.url_join("https://www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert ct.url_join("https://www.bad-actor.services", "/api") == "https://www.bad-actor.services/api"
        assert ct.url_join("https://www.bad-actor.services", "/api") == "https://www.bad-actor.services/api"
        assert ct.url_join("http://www.bad-actor.services", "/") == "http://www.bad-actor.services/"
        assert ct.url_join("https://www.bad-actor.services/", "/") == "https://www.bad-actor.services/"
        assert ct.url_join(
            "https://www.bad-actor.services/", "/", "api") == \
            "https://www.bad-actor.services/api"
        assert ct.url_join(
            "bad-actor-services_bad-actor-services-web_1:5000", "/api/proxies") == \
            "http://bad-actor-services_bad-actor-services-web_1:5000/api/proxies"

    def test_url_concat(self):
        """
        Tests the carpet_tools.url_concat() method, to make sure we're not adding any extra slashes or making weird
        urls.

        """
        assert ct.url_join("www.bad-actor.services", "api") == "http://www.bad-actor.services/api"
        assert ct.url_concat("https://www.bad-actor.services", "api") == "https://www.bad-actor.services/api"
        assert ct.url_concat("https://www.bad-actor.services", "/api") == "https://www.bad-actor.services/api"
        assert ct.url_concat(
            "https://www.bad-actor.services", "/api", "new//one") == "https://www.bad-actor.services/api/new/one"
        assert ct.url_concat("https://www.bad-actor.services", "/") == "https://www.bad-actor.services/"
        assert ct.url_concat("https://www.bad-actor.services/", "/") == "https://www.bad-actor.services/"

    def test_url_add_missing_protocol(self):
        """
        Tests CarpetBag.carpet_tools.url_add_missing_protocol() to make it adds protocals when it should.

        """
        assert ct.url_add_missing_protocol("https://www.bad-actor.services/") == "https://www.bad-actor.services/"
        assert ct.url_add_missing_protocol("www.bad-actor.services/") == "http://www.bad-actor.services/"
        assert ct.url_add_missing_protocol("http://www.bad-actor.services/") == "http://www.bad-actor.services/"
        assert ct.url_add_missing_protocol(
            "www.bad-actor.services/",
            default="https") == "https://www.bad-actor.services/"

    def test_url_disect(self):
        """
        Tests the carpet_tools.url_disect() method to make sure it pulls urls appart correctly.

        """
        url_pieces = ct.url_disect("https://www.bad-actor.services/some/url-thats-long?debug=True")

        assert url_pieces
        assert isinstance(url_pieces, dict)
        assert "original" in url_pieces
        assert "protocol" in url_pieces
        assert "domain" in url_pieces
        assert "subdomains" in url_pieces
        assert "tld" in url_pieces
        assert "port" in url_pieces
        assert "uri" in url_pieces
        assert "last" in url_pieces
        assert "params" in url_pieces

        assert url_pieces["protocol"] == "https"
        assert url_pieces["domain"] == "bad-actor.services"
        assert "www" in url_pieces["subdomains"]

        assert url_pieces["tld"] == "services"
        assert url_pieces["port"] == "443"
        assert url_pieces["uri"] == "/some/url-thats-long"
        assert url_pieces["last"] == "url-thats-long"
        assert isinstance(url_pieces["params"], dict)
        assert url_pieces["params"]["debug"] == "True"

    def test_url_subdomain(self):
        """
        Tests CarpetBag.carpet_tools.url_subdomain() to make sure we're find all url subdomains.

        """
        subdomains = ct.url_subdomain("https://www.bad-actor.services/some/url-thats-long?debug=True")
        assert isinstance(subdomains, list)
        assert len(subdomains) == 1
        subdomains = ct.url_subdomain("https://one.two.bad-actor.services/some/url-thats-long?debug=True")
        assert subdomains[0] == "one"
        assert subdomains[1] == "two"

    def test_url_params(self):
        """
        Tests CarpetBag.carpet_tools.url_params() to make sure we're getting url paramters.

        """
        params = ct.url_params("https://www.bad-actor.services/some/url-thats-long?debug=True&this=that")
        assert isinstance(params, dict)
        assert len(params) == 2
        assert params["debug"] == "True"
        assert params["this"] == "that"

    def test_date_to_json(self):
        """
        Tests the JSON date method to try and convert the information to JSON friendly output.

        """
        now = datetime.now()
        the_date = datetime(2018, 10, 13, 12, 12, 12)
        assert ct.date_to_json(the_date) == "2018-10-13 12:12:12"
        assert isinstance(ct.date_to_json(), str)
        assert ct.date_to_json()[:4] == str(now.year)

    def test_json_to_date(self):
        """
        Tests the CarpetBag.carpet_tools.json_to_date() method to see if we can make a propper python DateTime object
        from a JSON type date string.

        """
        json_date_string = "2018-10-13 12:12:12"
        the_date = ct.json_to_date(json_date_string)
        assert isinstance(the_date, datetime)
        assert the_date.year == 2018
        assert the_date.month == 10

    def test_url_domain(self):
        """
        Tests the CarpetBag.carpet_tools.url_domain() method to see if it properly picks the domain from a url.

        """
        assert ct.url_domain("http://www.google.com") == "google.com"
        assert ct.url_domain("http://localhost") == "localhost"
        assert ct.url_domain("http://192.168.1.19:5010") == "192.168.1.19"

    def test_url_port(self):
        """
        Tests the CarpetBag.carpet_tools.url_port() to make sure we're plucking the port from a url.

        """
        assert ct.url_port("https://www.bad-actor.services:5000/") == "5000"
        assert ct.url_port("https://www.bad-actor.services:502/") == "502"
        assert ct.url_port("https://www.bad-actor.services/") == "443"
        assert ct.url_port("http://www.bad-actor.services/") == "80"
        assert ct.url_port("http://www.bad-actor.services:50200") == "50200"

    def test_content_type_to_extension(self):
        """
        Tests the CarpetBag.carpet_tools.content_type_to_extension() method to make sure we're properly translatining.

        """
        assert ct.content_type_to_extension("image/jpg") == "jpg"
        assert ct.content_type_to_extension("image/jpeg") == "jpg"
        assert ct.content_type_to_extension("image/png",) == "png"
        assert ct.content_type_to_extension("text/css",) == "css"
        assert ct.content_type_to_extension("text/html") == "html"
        assert ct.content_type_to_extension("text/css") == "css"
        assert ct.content_type_to_extension("application/json") == "json"
        assert ct.content_type_to_extension("application/xml") == "xml"
        assert ct.content_type_to_extension("application/zip") == "zip"

    def test_extension_to_content_type(self):
        """
        Tests the CarpetBag.carpet_tools.extension_to_content_type() method to make sure we're properly translatining.

        """
        assert ct.extension_to_content_type("jpg") == "image/jpg"
        assert ct.extension_to_content_type("jpeg") == "image/jpg"
        assert ct.extension_to_content_type("png") == "image/png"
        ct.extension_to_content_type("css",) == "text/css"
        ct.extension_to_content_type("html") == "text/html"
        ct.extension_to_content_type("json") == "application/json"
        ct.extension_to_content_type("xml") == "application/xml"
        ct.extension_to_content_type("zip") == "application/zip"

# End File carpetbag/tests/test_carpet_tools.py
