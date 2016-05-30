# -*- coding: utf-8 -*-
import logging

from .StateMetaClass import StateMetaClass


class NoStateFoundException(Exception):
    pass


class BasicState(metaclass=StateMetaClass):
    tag = ''
    logger = logging.getLogger('State')
    logger.setLevel(logging.DEBUG)

    @staticmethod
    def create_transition(new_state_tag, **kwargs):
        if new_state_tag not in StateMetaClass.states:
            raise NoStateFoundException
        return new_state_tag, kwargs

    def __init__(self, user):
        self.user = user

    def enter(self, **kwargs):
        pass

    def update(self, message):
        pass

    def update_inline_req(self, inline_query):
        pass

    def update_inline_ans(self, inline_ans):
        pass

    def update_callback(self, callback):
        pass

    def exit(self):
        pass
