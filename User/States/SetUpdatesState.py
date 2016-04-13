import bot_strings
from .BasicState import BasicState
from . import StateTags


class SetUpdatesState(BasicState):
    tag = StateTags.SET_UPDATES

    def __init__(self, user):
        super().__init__(user)
        self.time = 0

    def enter(self):
        self.user.callback(bot_strings.set_updates_enter_message)

    def update(self, message):
        if message == bot_strings.cancel_id:
            return BasicState.create_transition(StateTags.MAIN)
        try:
            time = float(message)
            if self.user.check_time_correct(time):
                self.user.updates_duration = time
                self.user.callback(bot_strings.set_updates_success)
                return BasicState.create_transition(StateTags.MAIN)
            else:
                self.user.callback(bot_strings.set_updates_wrong_duration)
        except ValueError:
            self.user.callback(bot_strings.set_updates_wrong_time_str)
