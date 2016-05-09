# -*- coding: utf-8 -*-
from .StateMetaClass import StateMetaClass
from .BasicState import BasicState
from .NoneState import NoneState
from .MainState import MainState
from .SetUpdatesState import SetUpdatesState
from .AddLinkStates import AddLinkState, AddLinkTagState
from .SetPriceState import SetPriceState
from .SetMetroState import SetMetroState


class StateMachine:
    def __init__(self, user, initial_state_tag):
        self.states = {class_tag: class_constructor(user)
                       for class_tag, class_constructor
                       in StateMetaClass.states.items()}
        self.state = self.states[initial_state_tag]

    def change_state(self, params, silent=False):
        tag = params[0]
        args = params[1]
        if not silent:
            self.state.exit()
        self.state = self.states[tag]
        if not silent:
            self.state.enter(**args)

    def process_message(self, message):
        res = self.state.update(message)
        if res is not None:
            self.change_state(res)

    def process_inline_req(self, inline_query):
        self.state.update_inline_req(inline_query)

    def process_inline_ans(self, inline_ans):
        self.state.update_inline_ans(inline_ans)

    def process_callback(self, callback):
        self.state.update_callback(callback)

