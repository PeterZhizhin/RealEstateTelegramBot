# -*- coding: utf-8 -*-
from Queues import QueueWrapper
from Queues.ProducerConsumer.ProducerFactory import ProducerFactory


def callback(message, answer_callback):
    print("Got message")
    print(message)
    answer_callback("GOT MESSAGE")


if __name__ == "__main__":
    QueueWrapper.init()
    ProducerFactory.subscribe_producer('rabbitmq_test_req', 'rabbitmq_test_ans', callback)
    QueueWrapper.start(detach=False)
