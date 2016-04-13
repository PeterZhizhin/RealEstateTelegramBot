from ..BasicState import BasicState
from .. import StateTags
import bot_strings
import config
from datetime import datetime


class AddLinkTagState(BasicState):
    tag = StateTags.ADD_LINK_TAG

    def __init__(self, user):
        super().__init__(user)
        self.time = datetime.now()
        self.link = ''

    def enter(self, **wargs):
        self.user.callback(bot_strings.add_link_tag_enter)
        self.link = wargs['link']
        self.time = datetime.now()

    def update(self, message):
        if (datetime.now() - self.time).total_seconds() \
                > config.awaitance:
            self.user.callback(bot_strings.awaitance_time_exceeded)
            return BasicState.create_transition(StateTags.MAIN)
        if message in bot_strings.cancel_id:
            return BasicState.create_transition(StateTags.MAIN)
        if self.user.check_tag_correct(message):
            self.user.add_link(self.link, message)
            self.user.callback(bot_strings.add_link_success)
            if self.user.updates_duration is None:
                self.user.callback(bot_strings.updates_time_not_setted_up)
            return BasicState.create_transition(StateTags.MAIN)
        else:
            self.user.callback(bot_strings.add_link_tag_wrong_tag)

    def exit(self):
        self.time = 0
        self.link = ''
