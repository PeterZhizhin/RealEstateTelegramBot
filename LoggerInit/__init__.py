# -*- coding: utf-8 -*-
import logging

import config


def init_logging(log_filename):
    logger = logging.getLogger()
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('pika').setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(config.file_log_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(config.console_log_level)

    formatter = logging.Formatter(config.log_format)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
