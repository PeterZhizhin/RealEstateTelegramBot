# -*- coding: utf-8 -*-
import config
from Databases import Databases
import random
import string


class InvitesManager:
    db = Databases.get_invites_db()

    @staticmethod
    def generate_random_str(n):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                       for _ in range(n))

    @staticmethod
    def pull_invite(invite):
        invite = InvitesManager.db.find_one({'id': invite})
        if invite is not None:
            InvitesManager.db.delete_one({'_id': invite['_id']})
            return True
        return False

    @staticmethod
    def insert_invite(invite):
        InvitesManager.db.insert_one({'id': invite})

    @staticmethod
    def insert_random_invites(count, len):
        for _ in range(count):
            InvitesManager.insert_invite(InvitesManager.generate_random_str(len))

    @staticmethod
    def insert_many_invites(invites):
        InvitesManager.db.insert_many([{'id': invite} for invite in invites])

    @staticmethod
    def get_invites():
        return InvitesManager.db.find()

    @staticmethod
    def get_invite():
        return InvitesManager.db.find_one()

    @staticmethod
    def get_invites_list(count=config.default_invites_count):
        invites = [invite['id'] for invite in InvitesManager.get_invites()]
        if len(invites) < count:
            diff = config.default_invites_count - len(invites)
            InvitesManager.insert_random_invites(diff, config.invite_length)
            invites = [invite['id'] for invite in InvitesManager.get_invites()]
        return invites[:count]
