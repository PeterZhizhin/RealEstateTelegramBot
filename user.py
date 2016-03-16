import bot_data_bases
import cian_parser
import bot_strings
import config
import invites
import logging
import re
import datetime
logger = logging.getLogger('user')
logger.setLevel(logging.DEBUG)

class none_state:
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
            import ipdb
            ipdb.set_trace()
            self.user.authorized = True
            return 'main'
        else:
            self.user.callback(bot_strings.auth_failed + 
                    str(self.user.messages_before_ignore_left))

class main_state:
    def __init__(self, user):
        self.user = user
        self.state_changes = {
                    bot_strings.help_id: self.print_hello_message,
                    bot_strings.add_link_id: lambda: 'add_link_state',
                    bot_strings.get_links_id: self.get_links_answer,
                }

    def print_hello_message(self):
        self.user.callback(bot_strings.main_help)

    def get_links_answer(self):
        links = self.user.get_links()
        if len(links) == 0:
            self.user.callback(bot_strings.no_links_message)
            return
        total_string = bot_strings.current_links_message + '\n'
        for link in self.user.get_links():
            total_string += link + '\n'
        total_string = total_string.strip()
        self.user.callback(total_string)

    def enter(self):
        self.print_hello_message()

    def exit(self):
        pass

    def update(self, message):
        import ipdb
        ipdb.set_trace()
        if message in self.state_changes:
            return self.state_changes[message]()
        else:
            self.user.callback(bot_strings.wrong_command)

class add_link_state:
    def __init__(self, user):
        self.user = user
        self.time = 0

    def enter(self):
        self.user.callback(bot_strings.add_link_enter)
        self.time = datetime.now()

    def update(self, message):
        if (datetime.now() - self.time()).total_seconds()\
            < config.awaitance:
                return 'main'
        if self.check_url_correct(message):
            pass

    def exit(self):
        pass

class user:
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
                'none': none_state(self),
                'main': main_state(self),
                'add_link_state': add_link_state(self),
                }
        self.current_state_mark = 'none'
        if self._authorized:
            self.current_state = self.states['main']
        else:
            self.current_state = self.states['none']

    def unset_updates_handler_if_needed(self):
        if self.messages_before_ignore_left <= 0:
            self.process_message = self.null_process_message

    def pull_auth_message(self, message):
        self.messages_before_ignore_left -= 1
        if invites.pull_invite(message):
            return True
        self.unset_updates_handler_if_needed()
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
            self.db.update_one(self.db_filter, {'$set': {'auth': False},
                '$set': {'ignore_left': config.user_messages_before_ignore}})

    def get_links(self):
        return self.links

    def check_url_correct(self, link):
        return cian_parser.check_url_correct(link)

    def check_tag_correct(self, tag):
        return True

    def try_add_link(self, link, tag):
        if cian_parser.check_url_correct(link):
            logger.debug("Adding link of user " + self.user_id\
                    + " to database\n" + link +\
                    + " with tag " + tag)
            self.links.append(link)
            self.db.update_one(self.db_filter, 
                    {'$push': {'links': (link, tag)}})
            return True
        return False

    def change_state(self, new_state_str, silent=False):
        if not silent:
            self.current_state.exit()
        self.current_state = self.states[new_state_str]
        if not silent:
            self.current_state.enter()
        self.current_state_mark = new_state_str

    def null_process_message(self, message_text):
        pass

    def process_message(self, message_text):
        new_state = self.current_state.update(message_text)
        if new_state is not None:
            self.change_state(new_state)
