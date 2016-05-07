# -*- coding: utf-8 -*-
import config
from Parsers import CianParser
from Queues import QueueWrapper
from Queues.ProducerConsumer.ProducerFactory import ProducerFactory


def check_url_callback(message, answer_callback):
    url = message['url']
    result = CianParser.check_url_correct(url)
    answer_callback(result)
    return True


def parse_url_callback(message, answer_callback):
    url = message['url']
    if 'time' in message.keys():
        time = message['time']
        result = CianParser.get_new_offers(url, time)
    else:
        result = CianParser.get_new_offers(url)
    result = [offer['id'] for offer in result]
    answer_callback(result)
    return True


def main():
    QueueWrapper.init()
    ProducerFactory.subscribe_producer(config.check_url_queue_req_queue, config.check_url_queue_ans_queue,
                                       check_url_callback)
    ProducerFactory.subscribe_producer(config.parse_url_req_queue, config.parse_url_ans_queue,
                                       parse_url_callback)
    ProducerFactory.subscribe_producer(config.parse_all_moscow_req_queue, config.parse_all_moscow_ans_queue,
                                       parse_url_callback)
    QueueWrapper.start(detach=False)
