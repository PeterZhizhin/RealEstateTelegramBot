# -*- coding: utf-8 -*-
import json

import config
import requests

base_url = 'https://api.telegram.org/bot{api_key}/{method}'


def request(api_key, method_name, **kwargs):
    request_timeout = 30
    if 'timeout' in kwargs:
        request_timeout = 2 * int(kwargs['timeout'])
    kwargs = {key: json.dumps(value) if isinstance(value, (dict, list, tuple, set))
    else value for key, value in kwargs.items()}
    req = requests.post(
        'https://api.telegram.org/bot{api_key}/{method}'.format(
            api_key=api_key,
            method=method_name
        ),
        kwargs,
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


class BasicInlineResult:
    def __init__(self, answer_id, answer_title, resulted_text, answer_description=None):
        self.element = {
            'type': 'article',
            'id': str(answer_id),
            'title': str(answer_title),
            'input_message_content': {
                'message_text': str(resulted_text)
            }
        }
        if answer_description is not None:
            self.element['description'] = str(answer_description)

    def object(self):
        return self.element


class InlineAnswer:
    def __init__(self, origin_inline, results):
        self.inline_id = origin_inline['id']
        self.results = [result.object() for result in results]
        self.cache_time = None
        self.personal = None

    def set_personal(self):
        self.personal = True

    def set_cache_time(self, time):
        self.cache_time = int(time)

    def _to_dict(self):
        assert self.results is not None
        assert self.inline_id is not None
        result = {
            'inline_query_id': self.inline_id,
            'results': json.dumps(self.results),
        }
        if self.cache_time is not None:
            result['cache_time'] = self.cache_time
        if self.personal is not None:
            result['is_personal'] = self.personal
        return result

    def send(self, answer_method):
        result = self._to_dict()
        return answer_method(result)


class MessageFunctionObject:
    def __init__(self, send_msg_function, send_inline_ans_function,
                 edit_message_text_function, edit_reply_markup,
                 answer_callback_function,
                 chat_id):
        self.chat_id = chat_id
        self.send_msg_function = send_msg_function
        self.send_inline_ans_function = send_inline_ans_function
        self.edit_message_text_function = edit_message_text_function
        self.edit_reply_markup = edit_reply_markup
        self.answer_callback_function = answer_callback_function

    @staticmethod
    def get_inline_keyboard(markup_array):
        keyboard_array = []
        for array in markup_array:
            res_array = []
            for button in array:
                res_array.append({
                    'text': button[0],
                    'callback_data': button[1],
                })
            keyboard_array.append(res_array)
        return MessageFunctionObject.inline_keyboard(keyboard_array)

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

    def prepare_message(self, message_text=None, inline_markup=None, parse_mode=None,
                        disable_web_page_preview=False):
        msg = dict()
        msg['chat_id'] = self.chat_id
        if message_text is not None:
            msg['text'] = message_text
        if inline_markup is not None:
            msg['reply_markup'] = json.dumps(inline_markup)
        if parse_mode is not None:
            assert parse_mode in ('Markdown', 'HTML')
            msg['parse_mode'] = parse_mode
        if disable_web_page_preview:
            msg['disable_web_page_preview'] = True
        return msg

    def __send_one(self, message_text, inline_markup=None, parse_mode=None, disable_web_page_preview=False):
        msg = self.prepare_message(message_text, inline_markup, parse_mode, disable_web_page_preview)
        return self.send_msg_function(msg)

    def answer_inline(self, answer):
        return answer.send(self.send_inline_ans_function)

    def change_text(self, message_id, message_text, inline_markup=None, parse_mode=None):
        msg = self.prepare_message(message_text, inline_markup, parse_mode)
        msg['message_id'] = message_id
        return self.edit_message_text_function(msg)

    def answer_callback(self, callback_id, text=None, show_alert=False):
        msg = dict()
        msg['callback_query_id'] = callback_id
        if text is not None:
            msg['text'] = text
        if show_alert:
            msg['show_alert'] = True
        return self.answer_callback_function(msg)

    def change_message_markup(self, message_id, reply_markup=None):
        msg = {
            'chat_id': self.chat_id,
            'message_id': message_id,
        }
        if reply_markup is not None:
            msg['reply_markup'] = reply_markup
        return self.edit_reply_markup(msg)

    def __call__(self, message_text, inline_markup=None, parse_mode=None,
                 disable_web_page_preview=False):
        # Allows to split message to fit Telegram requirements
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
            res = self.__send_one(message, inline_markup, parse_mode, disable_web_page_preview)
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
        for query in r:
            ans = dict()
            if 'message' in query.keys():
                ans['type'] = 'message'
                ans['body'] = query['message']
                if 'text' not in ans['body'].keys():
                    ans['body']['text'] = ''
            elif 'inline_query' in query.keys():
                ans['type'] = 'inline_req'
                ans['body'] = query['inline_query']
            elif 'chosen_inline_result' in query.keys():
                ans['type'] = 'inline_res'
                ans['body'] = query['chosen_inline_result']
            elif 'callback_query' in query.keys():
                ans['type'] = 'callback'
                ans['body'] = query['callback_query']
            ans['uid'] = ans['body']['from']['id']
            yield ans

    def send_message(self, message):
        return safe_request(self.api_key, 'sendMessage',
                            **message)

    def send_inline_ans(self, answer):
        return safe_request(self.api_key, 'answerInlineQuery',
                            **answer)

    def edit_text(self, new_message):
        return safe_request(self.api_key, 'editMessageText',
                            **new_message)

    def edit_message_markup(self, params):
        return safe_request(self.api_key, 'editMessageReplyMarkup',
                            **params)

    def answer_callback(self, params):
        return safe_request(self.api_key, 'answerCallbackQuery',
                            **params)

    def return_callback(self, chat_id):
        return MessageFunctionObject(self.send_message, self.send_inline_ans,
                                     self.edit_text, self.edit_message_markup,
                                     self.answer_callback,
                                     chat_id)

