from bs4 import BeautifulSoup


class ParseResponse(object):

    def __init__(self, raw_content):
        self.raw_content = raw_content

    def get_title(self):
        soup = BeautifulSoup(self.raw_content, 'html.parser')
        return soup.title.string.strip()
