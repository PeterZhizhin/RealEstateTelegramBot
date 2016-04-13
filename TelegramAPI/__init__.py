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
    if request.status_code != 200:
        raise Exception('Telegram request code was not OK. Resulted code: {}'.format(request.status_code))
    if not request.json()['ok']:
        raise Exception('Telegram request \'ok\' field is not True')


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

    def __call__(self, message_text):
        self.msg['text'] = message_text
        res = self.send_msg_function(self.msg)
        self.clear_message()
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
