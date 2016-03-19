import bot_data_bases
import cian_parser
import bot_strings
import config
import invites
import logging
import re
from datetime import datetime

logger = logging.getLogger('user')
logger.setLevel(logging.DEBUG)


class StateTransitionCreator:
    @staticmethod
    def create_transition(new_state_tag, **wargs):
        return new_state_tag, wargs


class NoneState:
    def __init__(self, user):
        self.user = user

    def enter(self):
        self.user.logger.debug('Entered none mode for ' + self.user.user_id)
        self.user.callback(bot_strings.hello_message)

    def exit(self):
        self.user.callback(bot_strings.auth_finished)

    def update(self, message):
        if self.user.pull_auth_message(message.strip()):
            if message == bot_strings.start_id:
                self.user.callback(bot_strings.hello_message)
            self.user.authorized = True
            return StateTransitionCreator.create_transition('main')
        else:
            self.user.callback(bot_strings.auth_failed +
                               str(self.user.messages_before_ignore_left))


class MainState:
    def __init__(self, user):
        self.user = user
        self.state_changes = {
            bot_strings.help_id: self.print_hello_message,
            bot_strings.add_link_id: lambda:
            StateTransitionCreator.create_transition('add_link_state'),
            bot_strings.get_links_id: self.get_links_answer,
            bot_strings.set_updates_id: lambda:
            StateTransitionCreator.create_transition('set_updates_state'),
        }

    def print_hello_message(self):
        self.user.callback(bot_strings.main_help)

    def get_links_answer(self):
        links = self.user.get_links()
        if len(links) == 0:
            self.user.callback(bot_strings.no_links_message)
            return
        total_string = bot_strings.current_links_message + '\n'
        for link in links:
            total_string += link[1] + '\n'
        total_string = total_string.strip()
        self.user.callback(total_string)

    def enter(self):
        self.print_hello_message()

    def exit(self):
        pass

    def update(self, message):
        if message in self.state_changes:
            return self.state_changes[message]()
        else:
            self.user.callback(bot_strings.wrong_command)


class SetUpdatesState:
    def __init__(self, user):
        self.user = user
        self.time = 0

    def enter(self):
        self.user.callback()


class AddLinkState:
    def __init__(self, user):
        self.user = user
        self.time = datetime.now()

    def enter(self):
        self.user.callback(bot_strings.add_link_enter)
        self.time = datetime.now()

    def update(self, message):
        logger.debug("User " + str(self.user.user_id) + " adding link")
        if (datetime.now() - self.time).total_seconds() \
                > config.awaitance:
            self.user.callback(bot_strings.awaitance_time_exceeded)
            return StateTransitionCreator.create_transition('main')
        if message in bot_strings.cancel_id:
            return StateTransitionCreator.create_transition('main')
        if self.user.check_url_correct(message):
            logger.debug("User " + str(self.user.user_id) + " adding link " + message)
            return StateTransitionCreator.create_transition('get_link_tag', link=message)
        else:
            logger.debug("User " + str(self.user.user_id) + " adding link " + message + " was wrong")
            self.user.callback(bot_strings.add_link_failed)

    def exit(self):
        self.time = 0


class GetLinkTagState:
    def __init__(self, user):
        self.user = user
        self.time = 0
        self.link = datetime.now()

    def enter(self, **wargs):
        self.user.callback(bot_strings.add_link_tag_enter)
        self.link = wargs['link']
        self.time = datetime.now()

    def update(self, message):
        if (datetime.now() - self.time).total_seconds() \
                > config.awaitance:
            self.user.callback(bot_strings.awaitance_time_exceeded)
            return StateTransitionCreator.create_transition('main')
        if message in bot_strings.cancel_id:
            return StateTransitionCreator.create_transition('main')
        if self.user.check_tag_correct(message):
            self.user.try_add_link(self.link, message)
            self.user.callback(bot_strings.add_link_success)
            return StateTransitionCreator.create_transition('main')
        else:
            self.user.callback(bot_strings.add_link_tag_wrong_tag)

    def exit(self):
        self.time = 0
        self.link = ""


class User:
    def __init__(self, chat, callback):
        user_id = chat['id']
        # Getting info from db
        self.db_filter = {'id': user_id}
        db = bot_data_bases.get_users_db()
        data = db.find_one(self.db_filter)
        if data is None:
            logger.debug("User " + str(user_id) + " added to DB")
            data = config.default_user.copy()
            data['id'] = user_id
            db.insert_one(data)
        logger.debug("User " + str(user_id) + " " + str(data) + " inited")

        # Filling fields
        self.db = db
        self.user_id = user_id
        self._authorized = data['auth']
        if not self._authorized:
            self.messages_before_ignore_left = data['ignore_left']
        else:
            self.messages_before_ignore_left = config.user_messages_before_ignore
        self.links = data['links']

        self.callback = callback
        self.states = {
            'none': NoneState(self),
            'main': MainState(self),
            'add_link_state': AddLinkState(self),
            'get_link_tag': GetLinkTagState(self),
        }
        self.current_state_mark = 'none'
        if self._authorized:
            self.current_state = self.states['main']
        else:
            self.current_state = self.states['none']

    def pull_auth_message(self, message):
        self.messages_before_ignore_left -= 1
        if invites.pull_invite(message):
            return True
        self.db.update_one(self.db_filter, {'$inc': {'ignore_left': -1}})
        return False

    @property
    def authorized(self):
        return self._authorized

    @authorized.setter
    def authorized(self, value):
        self._authorized = value
        if value:
            self.db.update_one(self.db_filter, {'$set': {'auth': True},
                                                '$unset': {'ignore_left': ''}})
        else:
            self.db.update_one(self.db_filter, {'$set': {'auth': False,
                                                         'ignore_left': config.user_messages_before_ignore}})

    def get_links(self):
        return self.links

    @staticmethod
    def check_url_correct(link):
        return cian_parser.check_url_correct(link)

    @staticmethod
    def check_tag_correct(tag):
        return len(tag) < config.max_tag_len

    def try_add_link(self, link, tag):
        if cian_parser.check_url_correct(link):
            logger.debug("Adding link of user " + str(self.user_id) +
                         " to database\n" + link +
                         " with tag " + tag)
            self.links.append([link, tag])
            self.db.update_one(self.db_filter,
                               {'$push': {'links': (link, tag)}})
            return True
        return False

    def change_state(self, new_state, silent=False):
        new_state_str = new_state[0]
        new_state_params = new_state[1]
        if not silent:
            self.current_state.exit()
        self.current_state = self.states[new_state_str]
        if not silent:
            self.current_state.enter(**new_state_params)
        self.current_state_mark = new_state_str

    def null_process_message(self, message_text):
        pass

    def process_message(self, message_text):
        if self.messages_before_ignore_left > 0:
            new_state = self.current_state.update(message_text)
            if new_state is not None:
                self.change_state(new_state)
