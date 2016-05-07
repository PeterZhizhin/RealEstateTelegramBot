# -*- coding: utf-8 -*-
import logging

import config
from Parsers.CianParserProcess import main

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('pika').setLevel(logging.WARNING)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(config.console_log_level)

    formatter = logging.Formatter(config.log_format)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    main()
