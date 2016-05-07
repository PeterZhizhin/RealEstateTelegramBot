# -*- coding: utf-8 -*-
import config
import pika
import threading


class QueueWrapper:
    connection = None
    channel = None
    existing_queues = None
    existing_queues_lock = None

    @staticmethod
    def init():
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
    def start(detach=True):
        if detach:
            threading.Thread(target=QueueWrapper.channel.start_consuming).start()
        else:
            QueueWrapper.channel.start_consuming()

    @staticmethod
    def close():
        QueueWrapper.channel.close()
        QueueWrapper.connection.close()
        QueueWrapper.channel = None
        QueueWrapper.connection = None
