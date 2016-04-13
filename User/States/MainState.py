from .BasicState import BasicState
from . import StateTags
import bot_strings


class MainState(BasicState):
    tag = StateTags.MAIN

    def __init__(self, user):
        super().__init__(user)
        self.state_changes = {
            bot_strings.help_id: self.print_hello_message,
            bot_strings.add_link_id: lambda:
            BasicState.create_transition(StateTags.ADD_LINK),
            bot_strings.get_links_id: self.get_links_answer,
            bot_strings.set_updates_id: lambda:
            BasicState.create_transition(StateTags.SET_UPDATES),
        }

    def print_hello_message(self):
        self.user.callback(bot_strings.main_help)

    def get_links_answer(self):
        links = self.user.links
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

    def update(self, message):
        if message in self.state_changes:
            return self.state_changes[message]()
        else:
            self.user.callback(bot_strings.wrong_command)
