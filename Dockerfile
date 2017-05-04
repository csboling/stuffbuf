FROM python:alpine

RUN apk add --update \
    build-base \
    jpeg-dev \
    zlib-dev

ENV PORT=51966
ENV PIPELINE=png
RUN mkdir -p /src
VOLUME ["/src"]
WORKDIR /src

COPY requirements.txt /src/.
RUN pip install -r requirements.txt

COPY entrypoint.sh /src/
COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
