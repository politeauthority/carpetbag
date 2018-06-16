"""
"""
from bs4 import BeautifulSoup


class ParseResponse(object):

    def __init__(self, content):
        """
        Creates a new respose parser.

        :param content: The raw html content from the scraper.
        :type content: str
        """
        self.content = content
        self.soup = self._make_soup()

    def get_title(self):
        """
        Gets the title of the current content

        :returns: The page's title.
        :rtype: str
        """
        return self.soup.title.string.strip()

    def duckduckgo_results(self):
        """
        Parses a search result page from duckduckgo.com

        """
        links = self.soup.findAll("div", {"class": "result"})
        results = []
        for link in links:
            results.append(
                {
                    'title': link.h2.text.strip(),
                    'url': self._add_missing_protocol(link.find('a', {'class': 'result__url'}).text.strip())
                }
            )
        return results

    def _make_soup(self):
        return BeautifulSoup(self.content, 'html.parser')

    def _add_missing_protocol(self, url):
        """
        Adds the protocol 'http://' if a protocal is not present.

        :param url: The url that may or may not be missing a protocol.
        :type url: str
        :returns: Safe url with protocal.
        :rtype: str
        """
        if url[:8] == 'https://' or url[:7] == 'http://':
            return url
        else:
            return '%s%s' % ('http://', url)

# EndFile: scrapy/scrapy/parse_response.py
