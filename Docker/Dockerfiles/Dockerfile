FROM debian
MAINTAINER Peter Zhizhin <piter.zh@gmail.com>
RUN apt-get update
RUN apt-get install -y python3-lxml python3-pip
ADD requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
WORKDIR /source
