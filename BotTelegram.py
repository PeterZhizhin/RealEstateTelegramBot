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
        for query in bot.get_updates():
            pass
        while True:
            logger.debug("Getting updates")
            for query in bot.get_updates(timeout=30):
                type = query['type']
                body = query['body']
                user_id = query['uid']
                user = UserManager.get_or_create_user(user_id)
                if type == 'message':
                    logger.debug("Sending message to user {}".format(user_id))
                    user.process_message(body)
                elif type == 'inline_req':
                    logger.debug("Sending inline request to user {}".format(user_id))
                    user.process_inline_req(body)
                elif type == 'inline_ans':
                    logger.debug("Sending inline answer to user {}".format(user_id))
                    user.process_inline_ans(body)
                elif type == 'callback':
                    logger.debug("Sending callback to user {}".format(user_id))
                    user.process_callback(body)
    except KeyboardInterrupt:
        QueueWrapper.close()
