# -*- coding: utf-8 -*-
import logging

import config
from Queues.ProducerConsumer.ConsumerFactory import ConsumerFactory
from Queues.StraightQueue import StraightQueue
from . import User
import threading

logger = logging.getLogger("UserManager")


class UserManager:
    link_check_request_function = None
    users_dict = dict()
    dict_lock = threading.Lock()
    bot = None

    @staticmethod
    def link_check_acquired(info, result):
        logger.debug("Link checked for user {}".format(info['uid']))
        user = UserManager.get_or_create_user(info['uid'])
        url = info['url']
        tag = info['tag']
        user.link_add_callback(url, tag, result)
        return True

    @staticmethod
    def add_link_checking(user_id, link, tag):
        logger.debug("Checking link for user {}".format(user_id))
        UserManager.link_check_request_function({'uid': user_id,
                                                 'url': link,
                                                 'tag': tag}, {'url': link})

    @staticmethod
    def new_offers_callback(offers):
        user_id = offers['uid']
        new_links = offers['offers']
        user = UserManager.get_or_create_user(user_id)
        user.new_links_acquired_event(new_links)

    @staticmethod
    def init(bot):
        UserManager.bot = bot
        UserManager.link_check_request_function = ConsumerFactory.get_consumer(
            config.check_url_req_queue,
            config.check_url_ans_queue,
            UserManager.link_check_acquired)

        StraightQueue.subscribe_getter(config.new_offers_queue, UserManager.new_offers_callback)

    @staticmethod
    def delete_user(user_id):
        with UserManager.dict_lock:
            if user_id in UserManager.users_dict:
                del UserManager.users_dict[user_id]

    @staticmethod
    def get_or_create_user(user_id):
        with UserManager.dict_lock:
            if user_id in UserManager.users_dict:
                return UserManager.users_dict[user_id]

            u = User(user_id, UserManager.bot.return_callback(user_id), lambda: UserManager.delete_user(user_id))
            logger.debug("Added user with ID " + str(user_id))
            UserManager.users_dict[user_id] = u
            return u
