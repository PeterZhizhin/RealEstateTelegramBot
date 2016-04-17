FROM python:3.5
MAINTAINER Peter Zhizhin <piter.zh@gmail.com>
RUN wget http://nl.alpinelinux.org/alpine/edge/main/x86_64/py-lxml-3.5.0-r0.apk /tmp/py-lxml.apk
RUN apk add --allow-untrusted /tmp/py-lxml.apk
RUN apt-get update
RUN apt-get install -y python3-lxml
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
WORKDIR /source
CMD python3 /source/bot_main.py