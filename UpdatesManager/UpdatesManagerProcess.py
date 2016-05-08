# -*- coding: utf-8 -*-
import LoggerInit
import config
from Queues import QueueWrapper
from UpdatesManager import UpdatesManager


def main():
    LoggerInit.init_logging(config.log_update_manager_file)
    QueueWrapper.init()
    UpdatesManager.init_manager()
    QueueWrapper.start(detach=True)
    try:
        UpdatesManager.worker()
    except KeyboardInterrupt:
        QueueWrapper.close()
