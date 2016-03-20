import bot_strings
from .BasicState import BasicState
from . import state_tags


class SetUpdatesState(BasicState):
    tag = state_tags.SET_UPDATES

    def __init__(self, user):
        super().__init__(user)
        self.time = 0

    def enter(self):
        self.user.callback(bot_strings.set_updates_enter_message)

    def update(self, message):
        if message == bot_strings.cancel_id:
            return BasicState.create_transition(state_tags.MAIN)
        try:
            time = int(message)
            if self.user.check_time_correct(time):
                self.user.updates_duration = time
                self.user.callback(bot_strings.set_updates_success)
                return BasicState.create_transition(state_tags.MAIN)
            else:
                self.user.callback(bot_strings.set_updates_wrong_duration)
        except ValueError:
            self.user.callback(bot_strings.set_updates_wrong_time_str)
