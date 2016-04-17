import config
from .BasicState import BasicState
import bot_strings
from . import StateTags


class NoneState(BasicState):
    tag = StateTags.NONE

    def enter(self):
        self.user.logger.debug('Entered none mode for ' + self.user.user_id)
        self.user.callback(bot_strings.hello_message)

    def exit(self):
        self.user.callback(bot_strings.auth_finished)

    def authorize(self):
        self.user.authorized = True

    def update(self, message):
        if self.user.user_id == config.admin_id:
            self.user.callback(bot_strings.admin_hello)
            self.authorize()
            return BasicState.create_transition(StateTags.MAIN)
        if self.user.pull_auth_message(message.strip()):
            if message == bot_strings.start_id:
                self.user.callback(bot_strings.hello_message)
            self.authorize()
            return BasicState.create_transition(StateTags.MAIN)
        else:
            self.user.callback(bot_strings.auth_failed +
                               str(self.user.messages_before_ignore_left))
