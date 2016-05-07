# -*- coding: utf-8 -*-
import time

from Queues import QueueWrapper
from Queues.ProducerConsumer.ConsumerFactory import ConsumerFactory


def answer_got(msg_id, answer):
    print("Got answer", msg_id, answer)


if __name__ == "__main__":
    QueueWrapper.init()
    consumer = ConsumerFactory.get_consumer('rabbitmq_test_req', 'rabbitmq_test_ans', answer_got)
    QueueWrapper.start()
    for i in range(1000000000000000000000000000):
        consumer(i, "ECHO {}".format(i))
        time.sleep(0.0001)
