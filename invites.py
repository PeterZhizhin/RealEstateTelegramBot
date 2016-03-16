#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bot_data_bases
import random
import string
import config
from sys import stdin
db = None
def get_db():
    global db
    if db is None:
        db = bot_data_bases.get_invites_db()
    return db

def pull_invite(invite):
    db = get_db()
    invite = db.find_one({'id': invite})
    if invite is not None:
        db.delete_one({'_id': invite['_id']})
        return True
    return False

def generate_random_str(N):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Invite generator for realty telegram bot')
    parser.add_argument('-a', '--add', help='Add invites from stdin', action="store_true")
    parser.add_argument('-l', '--list', help='List all current available invites', default=1000, type=int)
    parser.add_argument('-r', '--random', help='Generate random invites', type=int)
    args = parser.parse_args()
    db = get_db()
    if args.list:
        for entry in db.find()[:args.list]:
            print(entry['id'])
    if args.add:
        if args.random is not None:
            for i in range(args.random):
                s = generate_random_str(config.invite_length)
                db.insert_one({'id': s})
                print(s, "added to invites")
        else:
            for line in stdin:
                db.insert_one({'id': line})
                print(line, "added to invites")
