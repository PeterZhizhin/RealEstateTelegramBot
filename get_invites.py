#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Databases.Invites import InvitesManager
from sys import stdin
import argparse
import config
import random
import string


def generate_random_str(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                   for _ in range(n))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Invite generator for realty telegram bot')
    parser.add_argument('-a', '--add', help='Add invites from stdin', action="store_true")
    parser.add_argument('-l', '--list', help='List all current available invites', default=1000, type=int)
    parser.add_argument('-r', '--random', help='Generate random invites', type=int)
    args = parser.parse_args()
    if args.list:
        for entry in InvitesManager.get_invites()[:args.list]:
            print(entry['id'])
    if args.add:
        invites = []
        if args.random is not None:
            for i in range(args.random):
                s = generate_random_str(config.invite_length)
                invites.append(s)
        else:
            for line in stdin:
                invites.append(line.strip())
        print("Adding invites:")
        print(*invites, sep='\n')
        InvitesManager.insert_many_invites(invites)
