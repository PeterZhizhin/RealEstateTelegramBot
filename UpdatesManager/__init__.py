# -*- coding: utf-8 -*-
import threading
import logging
from queue import Queue

import config
from Databases.UserLinks import LinksDBManager
from Parsers import CianParser
from User.UserManager import UserManager

logger = logging.getLogger("UpdatesManager")
logger.setLevel(logging.DEBUG)


class UpdatesManager:
    link_check_queue = Queue()
    link_check_callbacks = dict()
    link_check_callbacks_lock = threading.Lock()

    @staticmethod
    def push_callback_to_dict(callback_id, method):
        with UpdatesManager.link_check_callbacks_lock:
            UpdatesManager.link_check_callbacks[callback_id] = method

    @staticmethod
    def get_callback_from_dict(callback_id):
        with UpdatesManager.link_check_callbacks_lock:
            method = UpdatesManager.link_check_callbacks[callback_id]
            del UpdatesManager.link_check_callbacks[callback_id]
            return method

    current_id = 0

    @staticmethod
    def id_creator():
        UpdatesManager.current_id += 1
        return UpdatesManager.current_id

    @staticmethod
    def check_urls_worker():
        while True:
            request = UpdatesManager.link_check_queue.get(block=True)
            link = request['link']
            callback = UpdatesManager.get_callback_from_dict(request['callback'])
            callback(CianParser.check_url_correct(link))

    @staticmethod
    def worker():
        while True:
            for link in LinksDBManager.get_expired_links():
                LinksDBManager.update_expiration_time(link['_id'])
                logger.debug("Parsing offers for user " + str(link['id']))
                user = UserManager.get_or_create_user(link['id'])
                user.new_links_acquired_event(CianParser.get_new_offers(link['url'], time=max(config.cian_min_timeout,
                                                                                              link['frequency'] * 60)))

    @staticmethod
    def add_link_checking(link, callback):
        callback_id = UpdatesManager.id_creator()
        UpdatesManager.push_callback_to_dict(callback_id, callback)
        UpdatesManager.link_check_queue.put({'link': link, 'callback': callback_id})

    @staticmethod
    def init_manager():
        updates_thread = threading.Thread(target=UpdatesManager.worker)
        updates_thread.start()
        check_links_thread = threading.Thread(target=UpdatesManager.check_urls_worker)
        check_links_thread.start()
