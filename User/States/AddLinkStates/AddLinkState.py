# -*- coding: utf-8 -*-
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
        super().logger.debug("User {} adding link".format(self.user.user_id))
        if (datetime.now() - self.time).total_seconds() \
                > config.awaitance:
            self.user.callback(bot_strings.awaitance_time_exceeded)
            return BasicState.create_transition(StateTags.MAIN)
        if message in bot_strings.cancel_id:
            return BasicState.create_transition(StateTags.MAIN)
        super().logger.debug("User {} trying link {}".format(self.user.user_id, message))
        return BasicState.create_transition(StateTags.ADD_LINK_TAG, link=message)

    def exit(self):
        self.time = 0
