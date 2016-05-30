# -*- coding: utf-8 -*-
import bot_strings
from User.States import BasicState
from User.States import StateTags


class LinksMainState(BasicState):
    tag = StateTags.LINKS_MAIN

    def __init__(self, user):
        super().__init__(user)
        self.table = {
            bot_strings.back_label: lambda _: BasicState.create_transition(StateTags.MAIN),
            bot_strings.change_links_label: lambda _: BasicState.create_transition(StateTags.MAIN),
            bot_strings.change_updates_duration_label: lambda _: BasicState.create_transition(
                StateTags.LINKS_UPDATES_DURATION_STATE),
        }

    def print_message(self, invoke=False):
        link_tags = (link['tag'] for link in self.user.links)
        updates_duration = self.user.updates_duration
        self.user.set_menu(bot_strings.links_main_state_enter.format(updates_duration=updates_duration,
                                                                     links="\n".join(link_tags)),
                           bot_strings.links_main_state_keyboard,
                           invoke=invoke)

    def enter(self, invoke=False):
        self.print_message(invoke=invoke)

    def update(self, message):
        self.print_message(invoke=True)

    def update_callback(self, callback):
        if callback['data'] in self.table:
            return self.table[callback['data']](callback)

    def exit(self):
        pass
