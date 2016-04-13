#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib.parse import urlparse, parse_qs, urlencode

import config
import re
import requests
from Databases import Databases
from bs4 import BeautifulSoup as bs

table_cookies = {'serp_view_mode': 'table'}


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


def get_url(url):
    r = requests.get(url, cookies=table_cookies)
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


offer_info_class_lambda = lambda x: x is not None and x.startswith('objects_item_info_col_')


def parse_raw_offer(offer):
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
        entry_info['location']['metro']['name'] = metro_name
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
    user_id = re.match(".*id_user=([0-9]*)&", user_url).groups()[0]
    entry_info['user']['id'] = int(user_id)

    return entry_info


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
            return len(raw_offers) > 0
        except:
            return False


def get_new_offers(url, time=config.cian_default_timeout):
    db = Databases.get_flats_db()
    for offer in get_offers(url, time):
        entry_db = db.find_one({'id': offer['id']})
        if entry_db is None:
            db.insert_one(offer)
        yield offer


def get_count_of_offers(page_bs):
    if check_not_found(page_bs):
        return 0
    count_re = re.compile(".*?([1-9][0-9])\s*объявлен")
    count_entry = page_bs.find("meta", attrs={'content': lambda x: count_re.search(x)})
    assert count_entry is not None
    count = count_re.match(count_entry.attrs['content']).groups()[0]
    return int(count)


def get_offers(url, time):
    page_bs = get_url(change_params(url, totime=time, p=1))
    # Получаем число предложений
    num_of_offers = get_count_of_offers(page_bs)
    # Определяем по ним число страниц
    if num_of_offers == 0:
        return
    raw_offers = get_raw_offers(page_bs)
    yield from (parse_raw_offer(offer) for offer in raw_offers)
    num_of_offers -= len(raw_offers)
    i = 2
    while num_of_offers > 0:
        url = change_params(url, totime=time, p=i)
        raw_offers = get_raw_offers(get_url(url))
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
