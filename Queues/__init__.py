# -*- coding: utf-8 -*-
import logging

import config
import pika
import threading

logger = logging.getLogger("QueueWrapper")


class QueueWrapper:
    connection = None
    channel = None
    existing_queues = None
    existing_queues_lock = None
    consume_thread = None

    @staticmethod
    def init():
        logger.info("Initializing queue manager")
        base = "amqp://{username}:{password}@{host}:{port}"
        params = pika.URLParameters(base.format(username=config.rabbit_mq_user, password=config.rabbit_mq_pass,
                                                host=config.rabbit_mq_url, port=config.rabbit_mq_port))
        QueueWrapper.connection = pika.BlockingConnection(params)
        QueueWrapper.channel = QueueWrapper.connection.channel()
        QueueWrapper.channel.basic_qos(prefetch_count=1)
        QueueWrapper.existing_queues = set()
        QueueWrapper.existing_queues_lock = threading.Lock()

    @staticmethod
    def declare_queue(name):
        with QueueWrapper.existing_queues_lock:
            if name not in QueueWrapper.existing_queues:
                QueueWrapper.channel.queue_declare(queue=name)
                QueueWrapper.existing_queues.add(name)

    @staticmethod
    def subscribe_to_queue(callback, queue, no_ack=True):
        QueueWrapper.declare_queue(queue)
        QueueWrapper.channel.basic_consume(callback,
                                           queue=queue,
                                           no_ack=no_ack)

    @staticmethod
    def send_message(queue, message):
        QueueWrapper.declare_queue(queue)
        QueueWrapper.channel.basic_publish(exchange='',
                                           routing_key=queue,
                                           body=message)

    @staticmethod
    def clear_queue(queue):
        QueueWrapper.channel.queue_purge(queue=queue)

    @staticmethod
    def sleep(seconds):
        QueueWrapper.connection.sleep(seconds)

    @staticmethod
    def start_consuming_workaround(channel):
        while channel._consumer_infos:
            channel.connection.process_data_events(time_limit=5)

    @staticmethod
    def start(detach=True):
        if detach:
            QueueWrapper.consume_thread = threading.Thread(
                target=lambda: QueueWrapper.start_consuming_workaround(QueueWrapper.channel)
            )
            QueueWrapper.consume_thread.start()
        else:
            QueueWrapper.start_consuming_workaround(QueueWrapper.channel)

    @staticmethod
    def close():
        logger.info("Closing queue manager")
        logger.debug("Stop consuming")
        QueueWrapper.channel.stop_consuming()
        if QueueWrapper.consume_thread:
            logger.debug("Joining consume thread")
            QueueWrapper.consume_thread.join()
        QueueWrapper.channel.close()
        QueueWrapper.connection.close()
        QueueWrapper.channel = None
        QueueWrapper.connection = None
