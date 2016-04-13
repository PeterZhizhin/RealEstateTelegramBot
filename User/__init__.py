import logging

import bot_strings
import config
from Databases.Flats import LinksDBManager
from Databases.Invites import InvitesManager
from Parsers import CianParser
from .States import StateMachine, StateTags

logger = logging.getLogger('user')
logger.setLevel(logging.DEBUG)


class User:
    db = None

    @staticmethod
    def set_db(db):
        User.db = db

    def __init__(self, user_id, callback):
        # Getting info from db
        self.db_filter = {'id': user_id}
        data = User.db.find_one(self.db_filter)
        if data is None:
            logger.debug("User " + str(user_id) + " added to DB")
            data = config.default_user.copy()
            data['id'] = user_id
            User.db.insert_one(data)
        else:
            # In case of default user config
            # updates to avoid potential errors
            missed_keys_values = {key: value for key, value in
                                  config.default_user.items()
                                  if key not in data}
            if len(missed_keys_values) > 0:
                data.update(missed_keys_values)
                User.db.update_one(self.db_filter, {"$set": missed_keys_values})

        logger.debug("User " + str(user_id) + " " + str(data) + " inited")

        # Filling fields
        self.user_id = user_id
        self._authorized = data['auth']
        self.messages_before_ignore_left = data['ignore_left']
        self._updates_duration = data['updates_frequency']
        self._links = list(LinksDBManager.get_user_links(user_id))

        self.callback = callback
        self.state_machine = StateMachine(self,
                                          StateTags.MAIN if
                                          self._authorized
                                          else StateTags.NONE)

    def new_links_acquired_event(self, updates):
        logger.debug("Sending new offers to user " + str(self.user_id))
        received_links = set(User.db.find_one(self.db_filter)['received_links'])
        new_links = set()
        required_updates = (x for x in updates if x['id'] not in received_links)
        for update in required_updates:
            new_links.add(update['id'])
            self.callback.markdown = True
            metro = "{} ({})".format(update['location']['metro']['name'],
                                     update['location']['metro']['description']) \
                if 'metro' in update['location'] else "Нет"
            sizes_info = ", ".join(update['sizes'])
            message = bot_strings.base_for_sending_flat.format(metro=metro,
                                                               address=", ".join(update['location']['address']),
                                                               object=update['object'], sizes_total=sizes_info,
                                                               floor=update['floor'], price=update['price'][0],
                                                               price_info=update['price'][2], percent=update['fee'],
                                                               additional_info=", ".join(update['info']),
                                                               comment=update['comment'],
                                                               contacts=update['contacts'])
            self.callback(message)
        if len(new_links) > 0:
            User.db.update_one(self.db_filter, {"$pushAll": {'received_links': list(new_links)}})

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

        for link in LinksDBManager.get_user_links(self.user_id):
            LinksDBManager.update_frequency(link['_id'], value)

    @property
    def authorized(self):
        return self._authorized

    @authorized.setter
    def authorized(self, value):
        self._authorized = value
        if value:
            User.db.update_one(self.db_filter, {'$set': {'auth': True}})
        else:
            User.db.update_one(self.db_filter, {'$set': {'auth': False,
                                                         'ignore_left': config.user_messages_before_ignore}})

    @property
    def links(self):
        return self._links.values()

    @staticmethod
    def check_url_correct(link):
        return CianParser.check_url_correct(link)

    @staticmethod
    def check_tag_correct(tag):
        return len(tag) < config.max_tag_len

    @staticmethod
    def check_time_correct(time):
        return isinstance(time, int) and time >= config.min_time_update_len

    def add_link(self, link, tag):
        logger.debug("Adding link of user " + str(self.user_id) +
                     " to database\n" + link +
                     " with tag " + tag)
        self._links.append(LinksDBManager.add_user_link(self.user_id, link, tag,
                                                        self.updates_duration, 'CIAN'))

    def process_message(self, message_text):
        if self.messages_before_ignore_left > 0:
            self.state_machine.process_message(message_text)
