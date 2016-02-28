import bot_strings
import config
import invites
import logging
import re
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
        if self.user.messages_before_ignore_left > 0:
            self.user.messages_before_ignore_left -= 1
            if message == bot_strings.start_id:
                self.user.callback(bot_strings.hello_message)
            if invites.pull_invite(message.strip()):
                self.user.authorized = True
            else:
                self.user.callback(bot_strings.auth_failed + 
                        str(self.user.messages_before_ignore_left))
                if self.user.messages_before_ignore_left == 0:
                    self.user.callback(bot_strings.auth_totally_failed)

class main_state:
    def __init__(self, user):
        self.user = user
        self.command_regex = re.compile(r'^\/(\S+)\s*(.*)')

    def print_hello_message(self):
        self.user.callback(bot_strings.main_help)

    def enter(self):
        self.print_hello_message()

    def exit(self):
        pass

    def update(self, message):
        match = self.command_regex.match(message)
        if match is None:
            self.user.callback(bot_strings.wrong_command)
            return
        command, arg = match.groups()
        if command == bot_strings.help_id:
            self.print_hello_message()
        elif command == bot_strings.add_link_id:
            self.user.try_add_link(arg)
        elif command == bot_strings.get_links_id:
            links = self.user.get_links()
            if len(links) == 0:
                self.user.callback(bot_strings.no_links_message)
                return
            total_string = bot_strings.current_links_message + '\n'
            for link in self.user.get_links():
                total_string += link + '\n'
            total_string = total_string.strip()
            self.user.callback(total_string)
        else:
            self.user.callback(bot_strings.wrong_command)

class user:
    def __init__(self, chat, db, callback):
        user_id = str(chat['id'])
        # Getting info from db
        if user_id in db:
            data = db[user_id]
        else:
            logger.debug("User " + user_id + " added to DB")
            data = config.default_user.copy()
            db[user_id] = data
        logger.debug("User " + user_id + " " + str(data) + " inited")

        # Filling fields
        self.db = db
        self.user_id = int(user_id)
        self.authorized = data['auth']
        if not self.authorized:
            self.messages_before_ignore_left = data['ignore_left']
        else:
            self.messages_before_ignore_left = config.user_messages_before_ignore
        self.links = data['links']

        self.callback = callback
        self.states = {
                'none': none_state(self),
                'main': main_state(self),
                }
        self.current_state_mark = 'none'
        self.current_state = self.states['none']
        self.update_state(True)


    def get_links(self):
        return self.links

    def try_add_link(self, link):
        if self.check_link(link):
            self.add_link(link)
            return True
        return False

    def check_link(self, link):
        return True

    def add_link(self, link):
        self.links.append(link)

    def write_user_to_db(self):
        data = {}
        data['auth'] = self.authorized
        if not self.authorized:
            data['ignore_left'] = self.messages_before_ignore_left
        data['links'] = self.links
        self.db[str(self.user_id)] = data

    def change_state(self, new_state_str, silent=False):
        if not silent:
            self.current_state.exit()
        self.current_state = self.states[new_state_str]
        if not silent:
            self.current_state.enter()
        self.current_state_mark = new_state_str

    def update_state(self, silent=False):
        if not self.authorized and self.current_state_mark != 'none':
            self.change_state('none', silent)
            return
        if not self.authorized:
            return
        if self.authorized and self.current_state_mark == 'none':
            self.change_state('main', silent)
            return

    def process_message(self, message_text):
        self.current_state.update(message_text)
        self.update_state()
        self.write_user_to_db()
