set -e
docker-compose build --no-cache
docker-compose up -d
docker exec -it scrapy_scrape_1 python3 setup.py build
docker exec -it scrapy_scrape_1 python3 setup.py install
docker exec -it scrapy_scrape_1 pytest .
docker exec -it scrapy_scrape_1 flake8 -v
docker-compose stop

