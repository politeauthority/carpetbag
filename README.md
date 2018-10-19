# Scrapy
A multi faceted scraping swiss army knife, built on top of the python [Requests](http://docs.python-requests.org/en/master/) module. All primary HTTP methods return a Requests object back.

## What's it do
- Scrapy can rate limit outbound requests by setting the ```mininum_wait_time``` var. This makes sure to wait at least as long as this value, but if the time has already ellapsed (due to processing on your end etc.) the request will run.
- Can set a longer wait on connection failures before retry using the ```wait_and_retry_on_connection_error``` var.
- Can set more retry attemps on connection failure by setting the ```retries_on_connection_failure``` var.
- Set a random common browser user agent string for the session by using the ```use_random_user_agent()``` method.
- Fill a bag with free public proxy services from across the globe and direct traffic through them, using the ```use_random_public_proxy()``` method

## What will it do
- Change Identity - Reset the tor exit node and cycle User Agent strings.
- Make FlaskRestless queries - Simply send REST API commands using the FlaskRestless basic API structure.

## Basic Usage
Run scraper through a proxy service, though this is not required, proxy services will enhance Srapey's ability to reliable return a result
```python
from scrapy import Scrapy

scraper = Scrapy()
scraper.use_random_user_agent()
scraper.use_random_public_proxy()
news = scraper.get('https://www.google.com/news/')
if news.status_code >= 400:
    scraper.reset_identity()
    news = scraper.get('https://www.google.com/news/')
print(news.text)
print(news.status_code)
```

## Install
```bash
git clone https://github.com/politeauthority/scrapy.git
cd scrapy
pip install -r requirements.txt
python setup.py build
sudo python setup.py install
```

## Public Methods
- Scraper.**get(url, skip_ssl_verify=False)**
        The primary method of Scraper, grabs a url over a specified proxy, set by the self.poxies class var. If none specified will grab over the current servers internet connection.
    - **url**: _(str)_ The url to grab from the remote source.
    - **skip_ssl_verify** _(default: False)_: _(bool)_
- Scrapper.**check_tor()**
    Checks if the current client/ proxy is propperly configured for tor.

## Tor Usage
For best results, use Privoxy to connect to tor, using a docker container is a really easy way to accomplish this. I'm using [zeta0/alpine-tor](https://github.com/zuazo/alpine-tor-docker) to launch a docker container running tor with privoxy support already enabled, and another container for Scrapy, all ready to go. This is all happening in the docker-compose.yml, just run ```docker-compose up```. Then insdie the scrape container you would run something like...

    from scrapy import Scrapy

    scraper = Scrapy()
    scraper.proxy = {"http": "tor:8118", "https": "tor:8118"}
    if scraper.check_tor():
        print("Tor Check: Connected!\n")
        response = scrapper.get('http://rnslnjdb6lioal3d.onion/')
        print(reponse.text)
    else:
        print("Tor Check: Failed\n")
