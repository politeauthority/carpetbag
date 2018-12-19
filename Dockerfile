FROM frolvlad/alpine-python3

ENV BAD_ACTOR_URL = "http://www.bad-actor.services/"
COPY ./ /opt/carpetbag

RUN apk add --no-cache \
    bash \
    python3 \
    python3-dev \
    py-pip \
    gcc \
    musl-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /opt/carpetbag/


ADD ./ /opt/carpetbag
RUN pip3 install -r requirements.txt
RUN pip3 install -r tests/requirements.txt
