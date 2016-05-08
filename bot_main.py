#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

import LoggerInit
from Databases import Databases
import config
from Queues import QueueWrapper
from TelegramAPI import Telegram
from User import User
from UpdatesManager import UpdatesManager
from User.UserManager import UserManager

if __name__ == "__main__":
    logger = LoggerInit.init_logging(config.log_file)

    logger.info('Application started')
    bot = Telegram(config.api_key)
    UserManager.set_bot(bot)
    User.set_db(Databases.get_users_db())
    QueueWrapper.init()
    UpdatesManager.init_manager()
    QueueWrapper.start(detach=True)
    while True:
        logger.debug("Getting updates")
        for query in bot.get_updates(timeout=30):
            user = UserManager.get_or_create_user(query['chat']['id'])
            user.process_message(query['text'])
