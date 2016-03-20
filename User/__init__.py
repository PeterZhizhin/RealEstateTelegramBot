import logging
import config
from Databases.invites import InvitesManager
from Parsers import cian_parser
from .States import StateMachine, state_tags

logger = logging.getLogger('user')
logger.setLevel(logging.DEBUG)


class User:
    db = None

    @staticmethod
    def set_db(db):
        User.db = db

    def __init__(self, chat, callback):
        user_id = chat['id']
        # Getting info from db
        self.db_filter = {'id': user_id}
        data = User.db.find_one(self.db_filter)
        if data is None:
            logger.debug("User " + str(user_id) + " added to DB")
            data = config.default_user.copy()
            data['id'] = user_id
            User.db.insert_one(data)
        logger.debug("User " + str(user_id) + " " + str(data) + " inited")

        # Filling fields
        self.user_id = user_id
        self._authorized = data['auth']
        if not self._authorized:
            self.messages_before_ignore_left = data['ignore_left']
        else:
            self.messages_before_ignore_left = config.user_messages_before_ignore
            self._updates_duration = data['updates_frequency']
        self.links = data['links']

        self.callback = callback
        self.state_machine = StateMachine(self,
                                          state_tags.MAIN if
                                          self._authorized
                                          else state_tags.NONE)

    def pull_auth_message(self, message):
        self.messages_before_ignore_left -= 1
        if InvitesManager.pull_invite(message):
            return True
        User.db.update_one(self.db_filter, {'$inc': {'ignore_left': -1}})
        return False

    @property
    def updates_duration(self):
        return self._updates_duration

    @updates_duration.setter
    def updates_duration(self, value):
        self._updates_duration = value
        User.db.update_one(self.db_filter, {'$set': {'updates_frequency': value}})

    @property
    def authorized(self):
        return self._authorized

    @authorized.setter
    def authorized(self, value):
        self._authorized = value
        if value:
            User.db.update_one(self.db_filter, {'$set': {'auth': True},
                                                '$unset': {'ignore_left': ''}})
        else:
            User.db.update_one(self.db_filter, {'$set': {'auth': False,
                                                         'ignore_left': config.user_messages_before_ignore}})

    def get_links(self):
        return self.links

    @staticmethod
    def check_url_correct(link):
        return cian_parser.check_url_correct(link)

    @staticmethod
    def check_tag_correct(tag):
        return len(tag) < config.max_tag_len

    @staticmethod
    def check_time_correct(time):
        return isinstance(time, int) and time >= config.min_time_update_len

    def try_add_link(self, link, tag):
        if cian_parser.check_url_correct(link):
            logger.debug("Adding link of user " + str(self.user_id) +
                         " to database\n" + link +
                         " with tag " + tag)
            self.links.append([link, tag])
            User.db.update_one(self.db_filter,
                               {'$push': {'links': (link, tag)}})
            return True
        return False

    def process_message(self, message_text):
        if self.messages_before_ignore_left > 0:
            self.state_machine.process_message(message_text)
