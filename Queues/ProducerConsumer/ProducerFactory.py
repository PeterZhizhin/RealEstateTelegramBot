# -*- coding: utf-8 -*-
from Queues import QueueWrapper, dump_object, load_object


class ProducerFactory:
    @staticmethod
    def subscribe_producer(request_queue_name, answer_queue_name, request_callback):
        def answer_callback(msg_id, answer):
            total_answer = {
                'id': msg_id,
                'ans': answer,
            }
            QueueWrapper.send_message(answer_queue_name, dump_object(total_answer))

        def req_callback(ch, method, properties, body):
            body = load_object(body)
            ack = request_callback(body['req'], lambda answer: answer_callback(body['id'], answer))
            if ack is None:
                ack = True
            if ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag)

        QueueWrapper.subscribe_to_queue(callback=req_callback,
                                        queue=request_queue_name,
                                        no_ack=False)


