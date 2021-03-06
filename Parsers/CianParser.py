#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib.parse import urlparse, parse_qs, urlencode

import logging
import time
import config
import os
import re
import requests
from Databases import Databases
from bs4 import BeautifulSoup as bs

import datetime
import pytz

table_cookies = {'serp_view_mode': 'table'}
logger = logging.getLogger("CianParser")


def change_params(url, **kwargs):
    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query, keep_blank_values=True)
    for key, value in kwargs.items():
        qs[key] = value
    res = ''
    if parsed_url.scheme != '':
        res += parsed_url.scheme + '://'
    else:
        res += 'http://'
    if parsed_url.hostname is not None:
        res += parsed_url.hostname
    return res + parsed_url.path + '?' + urlencode(qs, doseq=True)


def get_url_id():
    return datetime.datetime.now().strftime("%c")


def get_url(url):
    r = requests.get(url, cookies=table_cookies)
    if config.debug_cian:
        location = 'url_responses/answer{}.html'.format(get_url_id())
        os.makedirs(os.path.dirname(location), exist_ok=True)
        with open(location, 'w') as f:
            f.write(r.text)
    if r.status_code != 200:
        return None
    return bs(r.text, 'lxml')


def get_raw_offers(bs_res):
    return bs_res.findAll('tr', {'class': 'offer_container'})


def fix_text(text):
    if text is None:
        return ''
    if hasattr(text, 'text'):
        text = text.text
    return ' '.join(text.split())


def write_to_database(entry_id, entry, db):
    entry_db = db.find_one({'id': entry_id})
    if entry_db is not None:
        if entry['url'] != entry_db['url']:
            print("Equal id, but different")
            print(entry)
            print(entry_db)
    else:
        db.insert_one(entry)


def offer_info_class_lambda(x):
    return x is not None and x.startswith('objects_item_info_col_')


timezone = pytz.timezone('Europe/Moscow')
months = ["январь", "февраль", "март", "апрель", "май",
          "июнь", "июль", "август", "сентябрь", "октябрь",
          "ноябрь", "декабрь"]


def parse_time(date, time):
    current_time = datetime.datetime.now(timezone)
    if date == 'сегодня':
        date = current_time.date()
    elif date == 'вчера':
        date = (current_time - datetime.timedelta(days=1)).date()
    else:
        date = date.split(' ')
        day = int(date[0])
        if len(date) == 3:
            year = int(date[2])
        else:
            year = current_time.year
        month = date[1].lower()
        for i, name in enumerate(months):
            if name.startswith(month):
                month = i + 1
                break
        date = datetime.date(year=year, day=day, month=month)

    time = [int(i) for i in time.split(':')]
    time = datetime.time(hour=time[0], minute=time[1])

    return datetime.datetime.combine(date=date, time=time)


def parse_raw_offer(offer):
    try:
        info = offer.findAll('td', {'class': offer_info_class_lambda}, recursive=False)
        info = [i.find('div', {'class': 'objects_item_info_col_w'}) for i in info]

        # Create dict of all entries
        entry_info = dict()

        # col_1 -- расположение
        entry_info['location'] = {}
        loc = info[0].find('input')
        coords = loc.attrs['value']
        entry_info['location']['coordinates'] = coords
        metro = info[0].find('div', {'class': 'objects_item_metro'})
        if metro.find('a') is not None:
            metro_name = fix_text(metro.find('a'))
            entry_info['location']['metro'] = {}
            entry_info['location']['metro']['name'] = metro_name.replace("м. ", "")
            metro_descr = fix_text(metro.find('span', {'class': 'objects_item_metro_comment'}))
            entry_info['location']['metro']['description'] = metro_descr

        address_bs = offer.findAll('div', {'class': 'objects_item_addr'})
        address_str = [fix_text(i) for i in address_bs]
        entry_info['location']['address'] = address_str

        # col_2 -- объект
        descr = fix_text(info[1])
        entry_info['object'] = descr

        # col_3 -- площадь
        sizes = [fix_text(i) for i in info[2].findAll('td')]
        entry_info['sizes'] = sizes

        # col_4 -- цена
        price_list = info[3].findAll('div', {'class': lambda x: x is None or 'complaint' not in x})
        price_list = [fix_text(i) for i in price_list]
        entry_info['price'] = price_list

        # col_5 -- процент
        percent = fix_text(info[4])
        entry_info['fee'] = percent

        # col_6 -- этаж
        floor = fix_text(info[5])
        entry_info['floor'] = floor

        # col_7 -- доп. сведения
        additional_info = [fix_text(i) for i in info[6].findAll('td')]
        entry_info['info'] = additional_info

        # col_8 -- контакты
        contacts = fix_text(info[7].find('a'))
        entry_info['contacts'] = contacts

        # col_9 -- комментарий
        comment = info[8].find('div', {'class': lambda x: x is not None and 'comment' in x})
        comment_text = fix_text(comment.contents[0])
        entry_info['comment'] = comment_text
        flat_url = comment.find('a', {'href': lambda x: x is not None}).attrs['href']
        entry_info['url'] = flat_url
        flat_id = re.match(".*\/([0-9]*)\/", flat_url).groups()[0]
        entry_info['id'] = int(flat_id)

        user_link = info[8].find('a', {'href': lambda x: x is not None and 'id_user' in x})
        entry_info['user'] = {}
        user_name = user_link.text
        entry_info['user']['name'] = user_name
        user_url = user_link.attrs['href']
        user_id = re.match(".*id_user=([0-9]+).*", user_url).groups()[0]
        entry_info['user']['id'] = int(user_id)

        # <span class="objects_item_dt_added">30 Апр, 22:12</span>
        raw_time = info[8].find('span', {'class': 'objects_item_dt_added'})
        raw_time = fix_text(raw_time).split(",")
        raw_time = parse_time(raw_time[0], raw_time[1])
        entry_info['time'] = raw_time

        actions = info[8].find('div', {'class': 'object_actions'})
        photos = actions.find('a')
        photos = fix_text(photos)
        photos = re.match("Фото \(([0-9]+)\)", photos)
        if photos is not None:
            photos = int(photos.groups()[0])
        else:
            photos = 0
        entry_info['photos_count'] = photos

        return entry_info
    except Exception as e:
        logger.error("There was an exception {}".format(e))
        logger.error("Error while parsing offer. Dumping object to file")
        with open("file_parse_error.html", 'w') as f:
            f.write(str(offer))


cian_url = 'cian.ru/cat.php'


def check_not_found(page_bs):
    not_found = page_bs.find("div", attrs={"class": "serps-header_nothing-found__title"})
    if not_found:
        return 'Ничего не найдено' in not_found.text
    return False


def check_url_correct(url):
    if cian_url in url:
        try:
            page_bs = get_url(change_params(url, totime=3000, p=1))
            raw_offers = get_raw_offers(page_bs)
            return True
        except:
            return False


def get_new_offers(url, time=config.cian_default_timeout):
    db = Databases.get_flats_db()
    ids = {}
    for offer in get_offers(url, time):
        if offer['id'] in ids.keys():
            old = ids[offer['id']]
            old = old.copy()
            if old != offer:
                logger.error("Different dicts: {}\n{}".format(offer, old))
        else:
            offer['seen_by_suspicious_validator'] = False
            offer['suspicious'] = False
            ids[offer['id']] = offer
            db.find_one_and_replace({'id': offer['id']}, offer, upsert=True)
            yield offer
    logger.info("Totally parsed {} real offers.".format(len(ids)))


def get_count_of_offers(page_bs):
    if check_not_found(page_bs):
        return 0
    count_re = re.compile(".*?([1-9][0-9]*)\s*объявлен")
    count_entry = fix_text(page_bs.find("title"))
    if count_entry is None:
        with open('wrong_bs.pkl', 'w') as f:
            f.write(str(page_bs))
        logger.warning("Wrong page_bs. Saved as wrong_bs.pkl")
    assert count_entry is not None
    count = count_re.match(count_entry).groups()[0]
    return int(count)


def safe_request(url):
    trials = 0
    page_bs = None
    while page_bs is None and trials < config.cian_trials_before_none:
        page_bs = get_url(url)
        if page_bs is not None:
            return page_bs
        logger.warning("Request wasn't successful!")
        with open('request{0}.sav'.format(trials), 'w') as f:
            f.write(str(page_bs))
        time.sleep(2)
        trials += 1
    logger.error("Total request didn't succeed :<")
    return None


def get_offers(raw_url, url_time):
    url = change_params(raw_url, totime=url_time, p=1)
    page_bs = safe_request(url)
    # Получаем число предложений
    num_of_offers = get_count_of_offers(page_bs)
    logger.debug("Parsing {} offers".format(num_of_offers))
    # Определяем по ним число страниц
    if num_of_offers == 0:
        return
    raw_offers = get_raw_offers(page_bs)
    yield from (parse_raw_offer(offer) for offer in raw_offers)
    num_of_offers -= len(raw_offers)
    i = 2
    while num_of_offers > 0:
        url = change_params(raw_url, totime=url_time, p=i)
        raw_offers = get_raw_offers(safe_request(url))
        logger.debug("Parsing {} page".format(i))
        yield from (parse_raw_offer(offer) for offer in raw_offers)
        num_of_offers -= len(raw_offers)
        i += 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='CIAN parser by URL')
    parser.add_argument('url', type=str, help='URL to parse')
    parser.add_argument('-t', '--time', type=int, help='Set time of last parsing',
                        default=360000000000000000000)
    args = parser.parse_args()
    db = Databases.get_flats_db()
    for info, info_id in get_offers(args.url, args.time):
        write_to_database(info_id, info, db)
