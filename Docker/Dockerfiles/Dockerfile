FROM debian
MAINTAINER Peter Zhizhin <piter.zh@gmail.com>
RUN apt-get update
RUN apt-get install -y python3-lxml python3-pip
ADD requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
WORKDIR /source
