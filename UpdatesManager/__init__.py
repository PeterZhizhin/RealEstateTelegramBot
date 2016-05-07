# -*- coding: utf-8 -*-
import threading
import logging
from queue import Queue

import config
from Databases.Flats import FlatsDB
from Databases.UserLinks import LinksDBManager
from Queues.ProducerConsumer.ConsumerFactory import ConsumerFactory
from User.UserManager import UserManager

logger = logging.getLogger("UpdatesManager")
logger.setLevel(logging.DEBUG)


class UpdatesManager:
    link_check_request_function = None
    link_update_request_function = None

    @staticmethod
    def link_check_acquired(info, result):
        user = UserManager.get_or_create_user(info['uid'])
        url = info['url']
        tag = info['tag']
        user.link_add_callback(url, tag, result)

    @staticmethod
    def link_updated_result(info, new_links):
        user = UserManager.get_or_create_user(info['uid'])
        offers = FlatsDB.get_flats(new_links)
        user.new_links_acquired_event(offers)

    @staticmethod
    def worker():
        while True:
            for link in LinksDBManager.get_expired_links():
                LinksDBManager.update_expiration_time(link['_id'])
                logger.debug("Parsing offers for user " + str(link['id']))
                user_info = link['id']
                UpdatesManager.link_update_request_function({'uid': user_info}, {'url': link['url'],
                                                                                'time': max(config.cian_min_timeout,
                                                                                            link['frequency'] * 60)})

    @staticmethod
    def add_link_checking(user_id, link, tag):
        UpdatesManager.link_check_request_function({'uid': user_id,
                                                    'url': link,
                                                    'tag': tag}, {'url': link})

    @staticmethod
    def init_manager():
        UpdatesManager.link_check_request_function = ConsumerFactory.get_consumer(config.check_url_queue_req_queue,
                                                                                  config.check_url_queue_ans_queue,
                                                                                  UpdatesManager.link_check_acquired)
        UpdatesManager.link_update_request_function = ConsumerFactory.get_consumer(config.parse_url_req_queue,
                                                                                   config.parse_url_ans_queue,
                                                                                   UpdatesManager.link_updated_result)
        updates_thread = threading.Thread(target=UpdatesManager.worker)
        updates_thread.start()
