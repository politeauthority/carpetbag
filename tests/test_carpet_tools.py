"""Tests Carpet Tools

"""
from carpetbag import carpet_tools


class TestCarpetTools(object):

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
