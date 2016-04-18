# -*- coding: utf-8 -*-
import json

import config
import requests

base_url = 'https://api.telegram.org/bot{api_key}/{method}'


def request(api_key, method_name, **wargs):
    request_timeout = 30
    if 'timeout' in wargs:
        request_timeout = 2 * int(wargs['timeout'])
    req = requests.post(
        'https://api.telegram.org/bot{api_key}/{method}'.format(
            api_key=api_key,
            method=method_name
        ),
        wargs,
        timeout=request_timeout
    )
    return req


def check_errors(request):
    if not request.json()['ok']:
        js = request.json()
        raise Exception(
            'Telegram request \'ok\' field is not True.\n Resulted status code: {}.\n Description: {}'.format(
                js['error_code'],
                js['description']))
    if request.status_code != 200:
        raise Exception('Telegram request code was not OK. Resulted code: {}'.format(request.status_code))


def safe_request(api_key, method_name, **wargs):
    r = request(api_key, method_name, **wargs)
    check_errors(r)
    return r.json()['result']


class MessageFunctionObject:
    def __init__(self, send_msg_function, chat_id):
        self.chat_id = chat_id
        self.send_msg_function = send_msg_function
        self.msg = dict()
        self.clear_message()

    def clear_message(self):
        self.msg = dict(chat_id=self.chat_id)

    @property
    def markdown(self):
        return self.msg.get('parse_mode', default='') == 'Markdown'

    @markdown.setter
    def markdown(self, value):
        if value:
            self.msg['parse_mode'] = 'Markdown'
        else:
            self.msg.pop('parse_mode', None)

    @property
    def html(self):
        return self.msg.get('parse_mode', default='') == 'HTML'

    @html.setter
    def html(self, value):
        if value:
            self.msg['parse_mode'] = 'HTML'
        else:
            self.msg.pop('parse_mode', None)

    def add_markup(self, markup):
        self.msg['reply_markup'] = json.dumps(markup)

    @staticmethod
    def inline_keyboard(keyboard):
        return {'inline_keyboard': keyboard}

    @staticmethod
    def inline_text(text):
        return {'text': text}

    @staticmethod
    def inline_url(text, url):
        a = MessageFunctionObject.inline_text(text)
        a['url'] = url
        return a

    def __send_one(self, message_text):
        self.msg['text'] = message_text.encode('utf-8')
        return self.send_msg_function(self.msg)

    def __call__(self, message_text):
        if len(message_text) == 0:
            return None
        if len(message_text) > config.telegram_max_length:
            messages = message_text.split("\n")
            total_messages = [""]
            for message in messages:
                if len(total_messages[-1]) + len(message) < config.telegram_max_length:
                    total_messages[-1] += message + "\n"
                else:
                    total_messages.append(message)
        else:
            total_messages = [message_text]
        res = None
        for message in total_messages:
            res = self.__send_one(message)
        self.clear_message()
        assert res is not None
        return res


class Telegram:
    def __init__(self, api_key):
        self.api_key = api_key
        self.lastUpdate = 0

    def get_updates(self, **wargs):
        wargs['offset'] = self.lastUpdate
        r = safe_request(self.api_key, 'getUpdates', **wargs)
        if len(r) > 0:
            self.lastUpdate = max(self.lastUpdate, max(rq['update_id'] + 1 for rq in r))
        yield from (rq['message'] for rq in r)

    def send_message(self, message):
        return safe_request(self.api_key, 'sendMessage',
                            **message)

    def return_callback(self, chat_id):
        return MessageFunctionObject(self.send_message, chat_id)
