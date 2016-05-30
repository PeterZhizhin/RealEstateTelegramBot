# -*- coding: utf-8 -*-
from User.States import BasicState
from User.States import StateTags


class SearchMainState(BasicState):
    tag = StateTags.SEARCH_MAIN

    def __init__(self, user):
        super().__init__(user)

    def enter(self):
        pass

    def update(self, message):
        pass

    def update_callback(self, callback):
        pass

    def exit(self):
        pass
