from ..BasicState import BasicState
from .. import StateTags
from _datetime import datetime
import bot_strings
import config


class AddLinkState(BasicState):
    tag = StateTags.ADD_LINK

    def __init__(self, user):
        super().__init__(user)
        self.time = datetime.now()

    def enter(self):
        self.user.callback(bot_strings.add_link_enter)
        self.time = datetime.now()

    def update(self, message):
        super().logger.debug("User " + str(self.user.user_id) + " adding link")
        if (datetime.now() - self.time).total_seconds() \
                > config.awaitance:
            self.user.callback(bot_strings.awaitance_time_exceeded)
            return BasicState.create_transition(StateTags.MAIN)
        if message in bot_strings.cancel_id:
            return BasicState.create_transition(StateTags.MAIN)
        if self.user.check_url_correct(message):
            super().logger.debug("User " + str(self.user.user_id) + " adding link " + message)
            return BasicState.create_transition(StateTags.ADD_LINK_TAG, link=message)
        else:
            super().logger.debug("User " + str(self.user.user_id) + " adding link " + message + " was wrong")
            self.user.callback(bot_strings.add_link_failed)

    def exit(self):
        self.time = 0
