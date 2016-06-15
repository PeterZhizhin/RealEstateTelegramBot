# -*- coding: utf-8 -*-
import config
from .BasicState import BasicState
import bot_strings
from . import StateTags


class NoneState(BasicState):
    tag = StateTags.NONE

    def __init__(self, user):
        super().__init__(user)

    def enter(self):
        self.user.logger.debug('Entered none mode for ' + self.user.user_id)
        self.user.callback(bot_strings.hello_message)

    def exit(self):
        self.user.callback(bot_strings.auth_finished)

    def authorize(self):
        self.user.authorized = True

    def update(self, message):
        # if message == bot_strings.start_id:
        if False:
            self.user.callback(bot_strings.hello_message)
        # elif self.user.pull_auth_message(message.strip()):
        elif True:
            self.authorize()
            return BasicState.create_transition(StateTags.MAIN)
        else:
            self.user.callback(bot_strings.auth_failed +
                               str(self.user.messages_before_ignore_left))

        if self.user.user_id == config.admin_id:
            self.user.callback(bot_strings.admin_hello)
            self.authorize()
            return BasicState.create_transition(StateTags.MAIN)
