#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as bs
import myrequests_cacher
import re

import pdb

table_cookies = {'serp_view_mode': 'table'}
def get_url(url):
    r = requests.get(url, cookies=table_cookies)
    return bs(r.text)

def get_raw_offers(bs_res):
    return bs_res.findAll('tr', {'class': 'offer_container'})

def fix_text(text):
    return ' '.join(text.split())

offer_info_class_lambda = lambda x: x is not None and x.startswith('objects_item_info_col_')
def parse_raw_offer(offer):
    info = offer.findAll('td', {'class': offer_info_class_lambda}, recursive=False)
    info = [i.find('div', {'class':'objects_item_info_col_w'}) for i in info]

    # col_1 -- расположение
    loc = info[0].find('input')
    coords = loc.attrs['value']
    metro = loc.find('div', {'class':'objects_item_metro'})
    if metro.find('a') is not None:
        metro_name = fix_text(metro.find('a').text)
        metro_descr = fix_text(metro.find('span', {'class':'objects_item_metro_comment'}).text)

    address_bs = loc.findAll('div', {'class': 'objects_item_addr'})
    address_str = [fix_text(i.text) for i in address_bs]

    # col_2 -- объект
    descr = fix_text(info[1].text)

    # col_3 -- площадь
    sizes = [fix_text(i.text) for i in info[2].findAll('td')]

    # col_4 -- цена
    price_list = info[3].findAll('div', {'class': lambda x: x is None or 'complaint' not in x})
    price_list = [fix_text(i.text) for i in price_list]

    # col_5 -- процент
    percent = fix_text(info[4].text)

    # col_6 -- этаж
    floor = fix_text(info[5].text)

    # col_7 -- доп. сведения
    additional_info = [fix_text(i.text) for i in info[6].findAll('td')]

    # col_8 -- контакты
    contacts = info[7].find('a').text

    # col_9 -- комментарий
    comment = info[8].find('div', {'class': lambda x: x is not None and 'comment' in x})
    comment_text = fix_text(comment.contents[0])
    flat_url = comment.find('a', {'href': lambda x: x is not None}).attrs['href']
    user_link = info[8].find('a', {'href': lambda x: x is not None and 'id_user' in x})
    user_name = user_link.text;
    user_url = user_link.attrs['href']
    user_id = re.match(".*id_user=([0-9]*)&", user_url).groups()[0]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CIAN parser by URL')
    parser.add_argument('url', type=str, help='URL to parse')
    args = parser.parse_args()
    res = get_raw_offers(get_url(args.url))
    for offer in res:
        parse_raw_offer(offer)
