import requests
base_url = 'https://api.telegram.org/bot{api_key}/{method}'
def request(api_key, method_name, **wargs):
    req = requests.post(
        'https://api.telegram.org/bot{api_key}/{method}'.format(
            api_key=api_key,
            method=method_name
        ),
        wargs,
        timeout=30
    )
    return req

def check_errors(request):
    if request.status_code != 200:
        raise Exception('Telegram request code was not OK.')
    if not request.json()['ok']:
        raise Exception('Telegram request \'ok\' field is not True')

def safe_request(api_key, method_name, **wargs):
    r = request(api_key, method_name, **wargs)
    check_errors(r)
    return r.json()['result']

class Callback:
    def __init__(self, telegram_api, chat_id):
        self.telegram = telegram_api
        self.chat_id = chat_id

    def function(self, message, **wargs):
        self.telegram.sendMessage(self.chat_id, message)

class Telegram:
    def __init__(self, api_key):
        self.api_key = api_key
        self.lastUpdate = 0

    def getUpdates(self):
        r = safe_request(self.api_key, 'getUpdates', offset=self.lastUpdate)
        if len(r) > 0:
            self.lastUpdate = max(self.lastUpdate, max(rq['update_id'] + 1 for rq in r))
        yield from (rq['message'] for rq in r)

    def sendMessage(self, chat_id, text):
        return safe_request(self.api_key, 'sendMessage',
                chat_id=chat_id, text=text)

    def return_callback(self, chat_id):
        return Callback(self, chat_id).function
