"""Test Scrapy
Run by using "pytest ." in the project root.

"""
from scrapy.parse_response import ParseResponse


class TestParseResponse(object):

    def test___init__(self):
        """
        Tests that the module init has correct default values.

        """
        pr = ParseResponse('test')
        assert pr.response == 'test'
