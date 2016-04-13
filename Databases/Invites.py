from Databases import Databases


class InvitesManager:
    db = Databases.get_invites_db()

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
    def insert_many_invites(invites):
        InvitesManager.db.insert_many([{'id': invite} for invite in invites])

    @staticmethod
    def get_invites():
        return InvitesManager.db.find()
