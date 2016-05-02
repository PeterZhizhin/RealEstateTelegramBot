# -*- coding: utf-8 -*-
import threading
import logging

import config
from Databases.UserLinks import LinksDBManager
from Parsers import CianParser
from User.UserManager import UserManager

logger = logging.getLogger("UpdatesManager")
logger.setLevel(logging.DEBUG)


class UpdatesManager:
    @staticmethod
    def worker():
        while True:
            for link in LinksDBManager.get_expired_links():
                LinksDBManager.update_expiration_time(link['_id'])
                logger.debug("Parsing offers for user " + str(link['id']))
                user = UserManager.get_or_create_user(link['id'])
                user.new_links_acquired_event(CianParser.get_new_offers(link['url'], time=max(config.cian_min_timeout,
                                                                                              link['frequency']*60)))

    @staticmethod
    def init_manager():
        updates_thread = threading.Thread(target=UpdatesManager.worker, daemon=True)
        updates_thread.start()
