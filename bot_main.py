#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from user import user
import config
import logging
import shelve
import telegram_api

def open_user_db():
    return shelve.open(config.users_db_filename)

def get_user_from_db(user_dict, db, chat, bot, logger):
    user_id = chat['id']
    if user_id in user_dict:
        return user_dict[user_id]
    logger.debug('Added user with id ' + str(user_id) + ' to dict')
    callback = bot.return_callback(user_id)
    u = user(chat, db, callback)
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

    bot = telegram_api.Telegram(config.api_key)

    user_dict = {}
    with open_user_db() as db:
        while True:
                for query in bot.getUpdates():
                    user = get_user_from_db(user_dict, db, query['chat'], bot, logger)
                    user.process_message(query['text'])
