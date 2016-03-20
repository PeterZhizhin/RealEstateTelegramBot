from .StateMetaClass import StateMetaClass
from .BasicState import BasicState
from .NoneState import NoneState
from .MainState import MainState
from .SetUpdatesState import SetUpdatesState
from .AddLinkStates import AddLinkState, AddLinkTagState


class StateMachine:
    def __init__(self, user, initial_state_tag):
        pass
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
