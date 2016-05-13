# -*- coding: utf-8 -*-
import logging

import time

import string

import config
from Databases import Databases
from Queues import QueueWrapper
from Queues.ProducerConsumer.ConsumerFactory import ConsumerFactory
from Queues.StraightQueue import StraightQueue
import threading

logger = logging.getLogger("GlobalParser")


class GlobalParser:
    links_res = dict()
    parse_request_function = None
    offers_send_function = None
    need_close = False
    thread = None
    flats_ids = []

    @staticmethod
    def fix_price(flat):
        price = flat['price'][0]
        price = "".join(c for c in price if c in string.digits)
        return int(price)

    @staticmethod
    def new_links_update():
        if len(GlobalParser.flats_ids) == 0:
            return
        logger.info("Filtering offers and sending them to queue")
        # Filter ids from duplicates
        flats = set(GlobalParser.flats_ids)
        # Get these flats from DB
        flats = list(Databases.get_flats_db().find({'id': {'$in': list(flats)},
                                                    'location.metro': {'$exists': True}},
                                                   {'id': 1,
                                                    'location.metro.name': 1,
                                                    'price': 1}))
        for flat in flats:
            flat['price'] = GlobalParser.fix_price(flat)
        # Get all users with their fields
        users = Databases.get_users_db().find({'max_price': {'$exists': True},
                                               'metro_stations': {'$exists': True}},
                                              {'id': 1,
                                               'max_price': 1,
                                               'metro_stations': 1})
        # For each user filter links they need
        for user in users:
            user_id = user['id']
            user_max_price = user['max_price']
            user_stations = set(user['metro_stations'])
            # Filter by stations
            good_flats = (flat for flat in flats if flat['location']['metro']['name'].lower() in user_stations)
            good_flats = (flat for flat in good_flats if flat['price'] <= user_max_price)
            good_flats = list(good_flats)
            if len(good_flats) > 0:
                message = {
                    'uid': user_id,
                    'offers': [flat['id'] for flat in good_flats],
                }
                logger.debug("Sending {} offers to user {}".format(len(good_flats), user_id))
                GlobalParser.offers_send_function(message)

    @staticmethod
    def link_parsed(info, result):
        if not GlobalParser.need_close:
            if info in GlobalParser.links_res.keys():
                GlobalParser.links_res[info] = True
            GlobalParser.flats_ids.extend(result)
            logger.debug("Parsed {} offers".format(len(result)))
        else:
            return False

    @staticmethod
    def safe_sleep(seconds):
        left = seconds
        while not GlobalParser.need_close and left > 0:
            left -= 1
            time.sleep(1)

    @staticmethod
    def work():
        while not GlobalParser.need_close:
            logger.debug("Started parsing process")
            GlobalParser.flats_ids = []
            GlobalParser.links_res = dict()
            for i, link in enumerate(config.links_to_parse):
                GlobalParser.links_res[i] = False
                GlobalParser.parse_request_function(i, {'url': link, 'time': 0})
            while not GlobalParser.need_close and \
                    not all(GlobalParser.links_res.values()):
                logger.debug("Waiting 10 seconds for new links result")
                GlobalParser.safe_sleep(10)
            GlobalParser.new_links_update()
            logger.debug("Sleeping {} seconds".format(config.parser_wait_time))
            GlobalParser.safe_sleep(config.parser_wait_time)

    @staticmethod
    def register():
        QueueWrapper.clear_queue(config.parse_all_moscow_req_queue)
        GlobalParser.parse_request_function = ConsumerFactory.get_consumer(config.parse_all_moscow_req_queue,
                                                                           config.parse_all_moscow_ans_queue,
                                                                           GlobalParser.link_parsed)
        GlobalParser.offers_send_function = StraightQueue.get_sender(config.new_offers_queue)
        GlobalParser.thread = threading.Thread(target=GlobalParser.work)
        GlobalParser.thread.start()

    @staticmethod
    def close_thread():
        GlobalParser.need_close = True
        GlobalParser.thread.join()
