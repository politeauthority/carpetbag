"""Tests ParseResponse

"""
from carpetbag.parse_response import ParseResponse

from .data.response_data import GoogleDotComResponse


class TestParseResponse(object):

    def test___init__(self):
        """
        Tests that the ParseResponse module init has correct default values.

        """
        r = GoogleDotComResponse()
        pr = ParseResponse(r)
        assert pr.response == r
        assert pr.content

    def test__get_title(self):
        r = GoogleDotComResponse()
        pr = ParseResponse(r)
        assert pr.get_title() == "Here's a title"

    def test__remove_protocol(self):
        """
        Tests the ParseResponse.remove_protocol() method to ensure it properly takes off http:// and https:// from a
        string. Keep in mind this only removes http:// and https:// protocals.

        """
        assert ParseResponse.remove_protocol("http://google.com") == "google.com"
        assert ParseResponse.remove_protocol("https://google.com") == "google.com"
        assert ParseResponse.remove_protocol("http://www.google.com") == "www.google.com"

# End File carpetbag/tests/test_parse_response.py
