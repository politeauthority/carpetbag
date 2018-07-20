# Scrapy
The python scraper for the rest of us. Based on the [Requests](http://docs.python-requests.org/en/master/) module.

## Install
```bash
git clone https://github.com/politeauthority/scrapy.git
cd scrapy
pip install -r requirements.txt
python setup.py build
sudo python setup.py install
```

## Basic Usage
Run scraper through a proxy service, though this is not required, proxy services will enhance Srapey's ability to reliable return a result
```python
from scrapy import Scrapy

scraper = Scrapy()
scraper.proxies = {"http": "localhost:8118", "https": "localhost:8118"}
news = scraper.get('https://www.google.com/news/')
print(news.text)
print(news.status_code)
```

## Tor Usage
For best results, use Privoxy to connect to tor, using a docker container is a really easy way to accomplish this. Use project x to launch a docker container running tor with privoxy support already enabled.
- Tor via Docker
    ```bash
    docker run \
           --name tor \
           -d \
           -p 8118:8118 \
           -p 2090:2090 \
           -e tors=25 \
           -e privoxy=1 \
           zeta0/alpine-tor
    ```
- Python Code
    ```python
    from scrapy import Scrapy

    scraper = Scrapy()
    scraper.proxies = {"http": "localhost:8118", "https": "localhost:8118"}
    if scraper.check_tor():
        print("Tor Check: Connected!\n")
        response = scrapper.get('http://rnslnjdb6lioal3d.onion/')
        print(reponse.text)
    else:
        print("Tor Check: Failed\n")
    ```

## Public Methods
- Scraper.**get(url, skip_ssl_verify=False)**
        The primary method of Scraper, grabs a url over a specified proxy, set by the self.poxies class var. If none specified will grab over the current servers internet connection.
    - **url**: _(str)_ The url to grab from the remote source.
    - **skip_ssl_verify** _(default: False)_: _(bool)_
- Scrapper.**check_tor()**
    Checks if the current client/ proxy is propperly configured for tor.
