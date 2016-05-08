#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import LoggerInit
from Databases import Databases
import config
from Queues import QueueWrapper
from TelegramAPI import Telegram
from User import User
from User.UserManager import UserManager

if __name__ == "__main__":
    logger = LoggerInit.init_logging(config.log_file)

    logger.info('Application started')
    QueueWrapper.init()
    bot = Telegram(config.api_key)
    UserManager.init(bot)
    User.init()
    QueueWrapper.start(detach=True)
    try:
        while True:
            logger.debug("Getting updates")
            for query in bot.get_updates(timeout=30):
                user = UserManager.get_or_create_user(query['chat']['id'])
                user.process_message(query['text'])
    except KeyboardInterrupt:
        QueueWrapper.close()
