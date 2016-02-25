FROM python:3.5
MAINTAINER Peter Zhizhin <piter.zh@gmail.com>
RUN pip install requests lxml requests-cache beautifulsoup4
CMD python3 bot/bot_main.py
