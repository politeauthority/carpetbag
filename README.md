# CarpetBag (v.0.0.5)
<img align="right" src="https://vol-1.nyc3.digitaloceanspaces.com/bad-actor.services/1-0xc/static/img/carpetbag.jpg">
A multi faceted scraping swiss army knife, built on top of the python [Requests](http://docs.python-requests.org/en/master/) module. All primary HTTP methods return a Requests object back.

## What's it do
- CarpetBag can rate limit outbound requests by setting the ```mininum_wait_time``` var. This makes sure to wait at least as long as this value, but if the time has already ellapsed (due to processing on your end etc.) the request will run.
- Can set a longer wait on connection failures before retry using the ```wait_and_retry_on_connection_error``` var.
- Can set more retry attemps on connection failure by setting the ```retries_on_connection_failure``` var.
- Set a random common browser user agent string for the session by using the ```use_random_user_agent()``` method.
- Fill a bag with free public proxy services from across the globe and direct traffic through them, using the ```use_random_public_proxy()``` method

## What will it do
- Change Identity - Reset the tor exit node and cycle User Agent strings.
- Make FlaskRestless queries - Simply send REST API commands using the FlaskRestless basic API structure.

## Basic Usage
To run the scraper through a proxy service, though this is not required, proxy services will enhance CarpetBag's ability to reliably return a result.
```python
from carpetbag import CarpetBag

bagger = CarpetBag()
bagger.use_random_user_agent()
bagger.use_random_public_proxy()
news = bagger.get("https://www.google.com/news/")
if news.status_code >= 400:
    bagger.reset_identity()
    news = bagger.get("https://www.google.com/news/")
print(news.text)
print(news.status_code)
```

## Install
```bash
git clone https://github.com/politeauthority/carpetbag.git
cd carpetbag
pip install -r requirements.txt
python setup.py build
sudo python setup.py install
```

## Common Usage
- #### **use_random_user_agent(val=True)**
    Sets a random, common browser's User Agent string as the bagger's User Agent string.
    This sets the class `self.random_user_agent` to `True`, the class defaults this var to `False`.
    This sets the `self.user_agent` var with the return of `CarpetBagger.get_new_user_agent()`

    ##### Params
    - **val:** (`bool`) Whether or not to enable random user agents.
    ##### Returns (`bool`)
    Returns a `bool` of `True` if we successfully made the bagger use random user agent, or `False` to stop using random user agents.
    **Example:** `Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:49.0) Gecko/20100101 Firefox/49.0`
    :rtype: bool
## Public HTTP verb Methods
- #### **get(url, payload)**
    The primary method of scraper, grabs a url over a specified proxy, set by the self.poxies class var. If none specified will grab over the current servers internet connection.
    ##### Params
    - **url**: _(str)_ The url to fetch.
    - **payload**: _(dict)_ This is data that will get url escaped and added to the end of a request. Mostly a convenience, not required.
    ##### Returns
    - **desc:** Provides a Requests request back from the url specified.
    - **type:** `<Request>` obj
- #### **post(url, payload)**
  Completly identical to .get, except for the post http verb. CarpetBag does this for all HTTP verbs.
    ##### Params
    - **url**: _(str)_ The url to fetch.
    - **payload**: _(dict)_ This is data that will get url escaped and added to the end of a request. Mostly a convenience, not required.
    ##### Returns
    - **desc:** Provides a Requests request back from the url specified.
    - **type:** `<Request>` obj
- #### **put(url, payload)**
  Completly identical to .get, except for the post http verb. CarpetBag does this for all HTTP verbs.
- #### **delete(url, payload)**
  Completly identical to .get, except for the post http verb. CarpetBag does this for all HTTP verbs.
## Tor Usage
For best results, use Privoxy to connect to tor, using a docker container is a really easy way to accomplish this. I'm using [zeta0/alpine-tor](https://github.com/zuazo/alpine-tor-docker) to launch a docker container running tor with privoxy support already enabled, and another container for CarpetBag, all ready to go. This is all happening in the docker-compose.yml, just run ```docker-compose up```. Then insdie the scrape container you would run something like...

    from carpetbag import CarpetBag

    bagger = CarpetBag()
    bagger.proxy = {"http": "tor:8118", "https": "tor:8118"}
    if bagger.check_tor():
        print("Tor Check: Connected!\n")
        response = bagger.get("http://rnslnjdb6lioal3d.onion/")
        print(reponse.text)
    else:
        print("Tor Check: Failed\n")
## Testing
The python pytest module is used as the unit test module. Some of the more difficult unit tests benifit from being run under the docker-compose instuctions. This makes sure there's a service running a tor proxy as well as other utilities needed to make all tests pass. Assuming that, the following commands should run, and pass.
```
docker-compose build
docker-compose up
docker exec -it carpetbag_carpetbag_1 bash
pytest
```
