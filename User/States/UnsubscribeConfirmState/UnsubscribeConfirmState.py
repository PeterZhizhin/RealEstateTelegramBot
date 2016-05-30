# -*- coding: utf-8 -*-
import bot_strings
from User.States import BasicState
from User.States import StateTags


class UnsubscribeConfirmState(BasicState):
    tag = StateTags.UNSUBSCRIBE_CONFIRM

    def __init__(self, user):
        super().__init__(user)
        self.table = {
            bot_strings.no_label: lambda _: BasicState.create_transition(StateTags.MAIN),
            bot_strings.yes_label: self.unsubscribe,
        }

    def unsubscribe(self, callback):
        self.user.clear_all()
        self.user.callback.answer_callback(callback['id'], text=bot_strings.unsubscribed_notify)
        return BasicState.create_transition(StateTags.MAIN)

    def print_confirm(self, invoke=False):
        self.user.set_menu(bot_strings.unsubscribe_confirm, bot_strings.unsubscribe_keyboard_label,
                           invoke=invoke)

    def enter(self):
        self.print_confirm()

    def update(self, message):
        self.print_confirm(invoke=True)

    def update_callback(self, callback):
        if callback['data'] in self.table:
            return self.table[callback['data']](callback)

    def exit(self):
        pass
