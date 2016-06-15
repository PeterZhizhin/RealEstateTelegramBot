# -*- coding: utf-8 -*-
import config
from Databases.Invites import InvitesManager
from TelegramAPI import BasicInlineResult, InlineAnswer
from .BasicState import BasicState
from . import StateTags
import bot_strings


class MainState(BasicState):
    tag = StateTags.MAIN

    def __init__(self, user):
        super().__init__(user)
        self.state_changes = {
            bot_strings.help_id: lambda: self.print_hello_message(invoke=True),
            bot_strings.add_link_id: lambda: BasicState.create_transition(StateTags.ADD_LINK),
            bot_strings.get_links_id: self.get_links_answer,
            bot_strings.set_updates_id: lambda: BasicState.create_transition(StateTags.SET_UPDATES),
            bot_strings.set_price_id: lambda: BasicState.create_transition(StateTags.SET_PRICE),
            bot_strings.set_stations_id: lambda: BasicState.create_transition(StateTags.SET_METRO),
            bot_strings.stop_id: self.user.delete_user,
        }
        if self.user.user_id == config.admin_id:
            self.state_changes[bot_strings.invoke_invites] = self.send_invites
        self.menu_changes = {
            bot_strings.main_links_label: lambda _: BasicState.create_transition(StateTags.LINKS_MAIN),
            bot_strings.main_unsubscribe_label: lambda _: BasicState.create_transition(StateTags.UNSUBSCRIBE_CONFIRM),
            bot_strings.main_search_label: lambda _: BasicState.create_transition(StateTags.SEARCH_MAIN),
        }

    def send_invites(self):
        invites = InvitesManager.get_invites_list()
        self.callback("\n".join(invites))

    def print_hello_message(self, invoke=False):
        self.user.callback(bot_strings.main_help)
        # self.user.set_menu(bot_strings.main_state_message, bot_strings.main_state_keyboard_label,
        #                   invoke=invoke)

    def get_links_answer(self):
        links = self.user.links
        if len(links) == 0:
            self.user.callback(bot_strings.no_links_message)
            return
        total_string = bot_strings.current_links_message + '\n'
        for link in links:
            total_string += link['tag'] + '\n'
        total_string = total_string.strip()
        self.user.callback(total_string)

    def enter(self, invoke=False):
        self.print_hello_message(invoke=invoke)

    def check_offer_tags(self, message):
        match = bot_strings.cian_cmd_regexp.match(message)
        if match is not None:
            offer_id = int(match.groups()[0])
            self.user.send_offer_info(offer_id)
            return True
        return False

    def update(self, message):
        message = message.strip()
        if message in self.state_changes:
            return self.state_changes[message]()
        elif not self.check_offer_tags(message):
            self.user.callback(bot_strings.wrong_command)

    def update_inline_req(self, inline_query):
        if self.user.user_id == config.admin_id:
            invites = InvitesManager.get_invites_list()
            answers = [BasicInlineResult(answer_id='invoke_invite_{}'.format(i),
                                         answer_title='Invite {}'.format(i),
                                         answer_description=invite,
                                         resulted_text=invite)
                       for i, invite in enumerate(invites, start=1)]
            answer = InlineAnswer(inline_query, answers)
            answer.personal = True
            answer.cache_time = 10
            self.user.callback.answer_inline(answer)

    def update_callback(self, callback):
        if callback['data'] in self.menu_changes:
            return self.menu_changes[callback['data']](callback)
        else:
            self.print_hello_message(invoke=True)
