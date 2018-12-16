"""Tests Carpet Tools

"""
from carpetbag import carpet_tools


class TestCarpetTools(object):

    def test__remove_protocol(self):
        """
        Tests the carpet_tools.remove_protocol() method to ensure it properly takes off http:// and https:// from a
        string. Keep in mind this only removes http:// and https:// protocals.

        """
        assert carpet_tools.remove_protocol("http://google.com") == "google.com"
        assert carpet_tools.remove_protocol("https://google.com") == "google.com"
        assert carpet_tools.remove_protocol("http://www.google.com") == "www.google.com"
