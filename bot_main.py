#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from Databases import Databases
import config
from TelegramAPI import Telegram
from User import User
from UpdatesManager import UpdatesManager
from User.UserManager import UserManager


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.getLogger('requests').setLevel(logging.WARNING)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(config.file_log_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(config.console_log_level)

    formatter = logging.Formatter(config.log_format)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.info('Application started')

    bot = Telegram(config.api_key)
    UserManager.set_bot(bot)
    UpdatesManager.init_manager()
    User.set_db(Databases.get_users_db())
    user_dict = {}
    while True:
        logger.debug("Getting updates")
        for query in bot.get_updates(timeout=30):
            user = UserManager.get_or_create_user(query['chat']['id'])
            user.process_message(query['text'])
