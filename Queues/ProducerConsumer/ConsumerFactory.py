# -*- coding: utf-8 -*-
from Queues import QueueWrapper
from Queues.ProducerConsumer import load_object, dump_object


class ConsumerFactory:
    @staticmethod
    def get_consumer(request_queue_name, answer_queue_name, answer_callback):
        def raw_answer_callback(ch, method, properties, body):
            body = load_object(body)
            ack = answer_callback(body['id'], body['ans'])
            if ack is None:
                ack = True
            if ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag)

        def write_msg(msg_id, request):
            message = {
                'id': msg_id,
                'req': request
            }
            packed = dump_object(message)
            QueueWrapper.send_message(request_queue_name, packed)

        QueueWrapper.subscribe_to_queue(callback=raw_answer_callback,
                                        queue=answer_queue_name,
                                        no_ack=False)
        return write_msg
