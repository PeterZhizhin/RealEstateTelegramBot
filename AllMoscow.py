import LoggerInit
import config
import pytz
from datetime import datetime
import time
import logging

from GlobalManager.GlobalParser import GlobalParser
from GlobalManager.SuspiciousChecker import SuspiciousChecker
from Queues import QueueWrapper
from Queues.ProducerConsumer.ConsumerFactory import ConsumerFactory

LoggerInit.init_logging(config.log_all_moscow_file)
logger = logging.getLogger("AllMoscowParser")

if __name__ == "__main__":
    QueueWrapper.init()
    GlobalParser.register()
    SuspiciousChecker.register()
    QueueWrapper.start(detach=True)
    try:
        while True:
            time.sleep(60 * 60 * 60)
    except KeyboardInterrupt:
        GlobalParser.close_thread()
        SuspiciousChecker.close_thread()
        QueueWrapper.close()
