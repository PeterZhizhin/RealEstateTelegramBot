#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import telegram_api
import shelve
import user
token = "169669071:AAHGq-UOgW-3EvyxPpCGLUVoQmkAHudqzkU"
bot = telegram_api.Telegram(token)

def open_user_db():
    shelve.open('users.bd')

def get_user_from_db(user_dict, db, user_id, bot):
    if user_id in user_dict:
        return user_dict[user_id]
    callback = bot.return_callback(user_id)
    if user_id in db.keys():
        data = db.get(user_id)
        u = user(user_id, data['auth'], data['links'], callback)
    else:
        data[user_id] = {'auth':False, 'links':None}
        u = user(user_id, False, None, callback)
    user_dict[user_id] = u
    return u

if __name__ == "__main__":
    user_dict = {}
    while True:
        with open_user_db() as db:
            for query in bot.getUpdates():
                user = get_user_from_db(user_dict, db, query['chat']['id'], bot)
                user.process_message(query['text'])
