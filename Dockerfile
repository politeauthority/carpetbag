FROM frolvlad/alpine-python3

COPY ./ /opt/scrapy

RUN apk add --no-cache \
    bash \
    python3 \
    python3-dev \
    py-pip \
    gcc \
    musl-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /opt/scrapy/


ADD ./ /opt/scrapy
RUN pip3 install -r requirements.txt
RUN pip3 install -r tests/requirements.txt


