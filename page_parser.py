#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, parse_qs, urlencode
import shelve
import myrequests_cacher
import re
import requests

import pdb

table_cookies = {'serp_view_mode': 'table'}
def change_params(url, **kwargs):
    parsed_url = urlparse(url)
    qs = parse_qs(parsed_url.query, keep_blank_values=True)
    for key, value in kwargs.items():
        qs[key] = value
    return parsed_url.scheme + '://' + parsed_url.hostname +\
        parsed_url.path + '?' + urlencode(qs, doseq=True)

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

def create_database():
    return shelve.open('flats.db')

def write_to_database(entry_id, entry, db):
    if entry_id in db.keys():
        if entry['url'] != db.get(entry_id)['url']:
            print("Equal id, but different")
            print(entry)
            print(db.get(entry_id))
    else:
        db[entry_id] = entry

def get_count_of_offers(raw_page):
    return int(raw_page.find('div', {'class': 'serp-above__count'}).find('strong').text)

offer_info_class_lambda = lambda x: x is not None and x.startswith('objects_item_info_col_')
def parse_raw_offer(offer):
    info = offer.findAll('td', {'class': offer_info_class_lambda}, recursive=False)
    info = [i.find('div', {'class':'objects_item_info_col_w'}) for i in info]

    # Create dict of all entries
    entry_info = {}

    # col_1 -- расположение
    entry_info['location'] = {}
    loc = info[0].find('input')
    coords = loc.attrs['value']
    metro = info[0].find('div', {'class':'objects_item_metro'})
    if metro.find('a') is not None:
        metro_name = fix_text(metro.find('a'))
        entry_info['location']['metro'] = {}
        entry_info['location']['metro']['name'] = metro_name
        metro_descr = fix_text(metro.find('span', {'class':'objects_item_metro_comment'}))
        entry_info['location']['metro']['description'] = metro_descr

    address_bs = loc.findAll('div', {'class': 'objects_item_addr'})
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
    user_name = user_link.text;
    entry_info['user']['name'] = user_name
    user_url = user_link.attrs['href']
    user_id = re.match(".*id_user=([0-9]*)&", user_url).groups()[0]
    entry_info['user']['id'] = int(user_id)

    return entry_info, flat_id

def get_offers(url, time):
    page_bs = get_url(change_params(url, to_time=time, p=1))
    # Получаем число предложений
    num_of_offers = get_count_of_offers(page_bs)
    # Определяем по ним число страниц
    raw_offers = get_raw_offers(page_bs)
    pages = num_of_offers // len(raw_offers)
    print("Pages total", pages)
    yield from (parse_raw_offer(offer) for offer in raw_offers)
    for i in range(2, pages+1):
        print("Page", i)
        url = change_params(url, to_time=time, p=i)
        raw_offers = get_raw_offers(get_url(url))
        yield from (parse_raw_offer(offer) for offer in raw_offers)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CIAN parser by URL')
    parser.add_argument('url', type=str, help='URL to parse')
    parser.add_argument('-t', '--time', type=int, help='Set time of last parsing',
            default=360000000000000000000)
    args = parser.parse_args()
    with create_database() as db:
        for info, info_id in get_offers(args.url, args.time):
            write_to_database(info_id, info, db)
