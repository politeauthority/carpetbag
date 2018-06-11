from scrapy.scrapy import Scrapy

scraper = Scrapy()

# Set the proxies for Scrapy to use, in this example we're connecting over privoxy which is routing traffic through tor.
scraper.proxies = {"http": "localhost:8118", "https": "localhost:8118"}

# I've had issues with certs from LetsEncrypt not passing cert checks.
# Set skip_ssl_verify high and we'll try once to get verify the cert, and if that fails go ahead with the request anyways.
scraper.skip_ssl_verify = True

# Check if the torproject.org to see if tor is setup and cofigured properly. 
if scraper.check_tor():
    print("Tor Check: Connected!\n")
else:
    print("Tor Check: Failed\n")

# Get the current outbound ip
print("Current outbound ip: %s" % scraper.get_outbound_ip())

x = scraper.get('http://rnslnjdb6lioal3d.onion/')

news = scraper.get('https://www.google.com/news/')
print(news.text)
print(news.status_code)

