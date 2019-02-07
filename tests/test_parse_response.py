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

# End File carpetbag/tests/test_parse_response.py
