# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Databases.Invites import InvitesManager
from sys import stdin
import argparse
import config

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
        if args.random is not None:
            InvitesManager.insert_random_invites(args.random, config.invite_length)
        else:
            invites = []
            for line in stdin:
                invites.append(line.strip())
            print("Adding invites:")
            print(*invites, sep='\n')
            InvitesManager.insert_many_invites(invites)
