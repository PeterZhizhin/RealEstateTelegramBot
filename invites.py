#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shelve
import random
import string
import config
from sys import stdin
db = None
def get_db():
    global db
    if db is None:
        db = shelve.open('invites.db')
    return db

def pull_invite(invite):
    db = get_db()
    if invite in db:
        del db[invite]
        return True
    return False

def generate_random_str(N):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Invite generator for realty telegram bot')
    parser.add_argument('-a', '--add', help='Add invites from stdin', action="store_true")
    parser.add_argument('-l', '--list', help='List all current available invites', action="store_true")
    parser.add_argument('-r', '--random', help='Generate random invites', type=int)
    args = parser.parse_args()
    with get_db() as db:
        if args.list:
            for key in db.keys():
                print(key)
        if args.add:
            if args.random is not None:
                for i in range(args.random):
                    s = generate_random_str(config.invite_length)
                    db[s] = True
                    print(s, "added to invites")
            else:
                for line in stdin:
                    db[line] = True
                    print(line, "added to invites")
