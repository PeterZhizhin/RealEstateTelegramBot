# -*- coding: utf-8 -*-
import bot_strings
import config
from TelegramAPI import BasicInlineResult, InlineAnswer
from .BasicState import BasicState
from . import StateTags


class SetPriceState(BasicState):
    tag = StateTags.SET_PRICE

    def __init__(self, user):
        super().__init__(user)

    def enter(self):
        self.user.callback(bot_strings.set_price_enter_message)

    def update(self, message):
        if message == bot_strings.cancel_id:
            return BasicState.create_transition(StateTags.MAIN)
        try:
            price = int(message)
            self.user.max_price = price
            self.user.callback(bot_strings.set_price_success)
            return BasicState.create_transition(StateTags.MAIN)
        except ValueError:
            self.user.callback(bot_strings.set_price_wrong_price)
