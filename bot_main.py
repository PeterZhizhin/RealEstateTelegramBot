#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging


from Databases import Databases
import config
from TelegramAPI import Telegram
from User import User


def get_user(user_dict, chat, bot, logger):
    user_id = chat['id']
    if user_id in user_dict:
        return user_dict[user_id]
    logger.debug('Added user with id ' + str(user_id) + ' to dict')
    callback = bot.return_callback(user_id)
    u = User(chat, callback)
    user_dict[user_id] = u
    return u


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

    User.set_db(Databases.get_users_db())

    user_dict = {}
    while True:
        logger.debug("Getting updates")
        for query in bot.get_updates(timeout=30):
            user = get_user(user_dict, query['chat'], bot, logger)
            user.process_message(query['text'])