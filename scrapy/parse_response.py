"""Parse Response
Handles parsing various html pages.

"""
from bs4 import BeautifulSoup
import tld


class ParseResponse(object):

    def __init__(self, response=None):
        """
        Creates a new respose parser.

        :param response: The response from the Requests module
        :type response: <Requests>
        """
        self.response = response
        self.soup = self._make_soup()

    def get_title(self):
        """
        Gets the title of the current content

        :returns: The page's title.
        :rtype: str
        """
        if not self.soup:
            return ''
        elif not self.soup.title:
            return ''
        elif not self.soup.title.string:
            return ''
        return self.soup.title.string.strip()

    def get_links(self):
        """

        """
        local_site = tld.get_tld(self.response.url)
        anchors = self.soup.findAll("a")

        ret = {
            'local': [],
            'remote': []
        }
        for anchor in anchors:
            if local_site in anchor['href'] and anchor['href'] not in ret['local']:
                ret['local'].append(anchor['href'])
            elif anchor['href'] not in ret['remote']:
                ret['remote'].append(anchor['href'])
        return ret

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
                    'description': link.find('a', {'class': 'result__snippet'}).text.strip(),
                    'url': self.add_missing_protocol(link.find('a', {'class': 'result__url'}).text.strip())
                }
            )
        return results

    @staticmethod
    def add_missing_protocol(url):
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

    @staticmethod
    def remove_protocol(url):
        """
        Adds the protocol 'http://' if a protocal is not present.

        :param url: The url that may or may not be missing a protocol.
        :type url: str
        :returns: Safe url with protocal.
        :rtype: str
        """

        if url[:8] == 'https://' or url[:7] == 'http://':
            return url.replace('/')
        else:
            return '%s%s' % ('http://', url)

    def _make_soup(self):
        """
        Converts the self.content var into soup.

        """
        if self.response:
            self.content = self.response.text
        if not self.content:
            return None
        return BeautifulSoup(self.content, 'html.parser')

# EndFile: scrapy/scrapy/parse_response.py
