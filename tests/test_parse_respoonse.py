"""Test Scrapy
Run by using "pytest ." in the project root.

"""
from scrapy.parse_response import ParseResponse

from .data.response_data import Response


class TestParseResponse(object):

    def test___init__(self):
        """
        Tests that the module init has correct default values.

        """
        r = Response()
        pr = ParseResponse(r)
        assert pr.response == r
        assert pr.content

    def test__get_title(self):
        r = Response()
        pr = ParseResponse(r)
        assert pr.get_title() == "Here's a title"

    def test__remove_protocol(self):
        assert ParseResponse.remove_protocol('http://google.com') == 'google.com'
        assert ParseResponse.remove_protocol('https://google.com') == 'google.com'
        assert ParseResponse.remove_protocol('http://www.google.com') == 'www.google.com'
