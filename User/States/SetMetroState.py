# -*- coding: utf-8 -*-
import bot_strings
import config
from TelegramAPI import BasicInlineResult, InlineAnswer
from . import StateTags
from .BasicState import BasicState


class SetMetroState(BasicState):
    tag = StateTags.SET_METRO
    all_metro_stations = bot_strings.station_names
    map_lowered_to_normal = {st.lower(): st for st in all_metro_stations}

    def __init__(self, user):
        super().__init__(user)

    def print_user_stations(self):
        user_stations = [SetMetroState.map_lowered_to_normal[st]
                         for st in self.user.get_metro_stations()]
        if len(user_stations) > 0:
            self.user.callback(bot_strings.current_stations_base.format(", ".join(user_stations)))

    def enter(self, **kwargs):
        self.user.callback(bot_strings.set_stations_enter)
        self.print_user_stations()

    def update(self, message):
        if message == bot_strings.stop_id:
            return BasicState.create_transition(StateTags.MAIN)
        elif message == bot_strings.clear_stations_id:
            self.user.clear_stations()
            self.user.callback(bot_strings.clear_stations_message)
            return

        lower_message = message.lower()
        if lower_message in SetMetroState.map_lowered_to_normal.keys():
            user_stations = self.user.get_metro_stations()
            if lower_message in user_stations:
                self.user.remove_station(lower_message)
                self.user.callback(bot_strings.station_deleted_message.format(message))
            else:
                self.user.add_station(lower_message)
                self.user.callback(bot_strings.station_added_message.format(message))

            if len(self.user.get_metro_stations()) == 0:
                self.user.callback(bot_strings.deleted_last_station)
            else:
                self.print_user_stations()
        else:
            self.user.callback(bot_strings.station_not_found_message.format(message))

    def exit(self):
        pass

    def update_inline_req(self, inline_query):
        message = inline_query['query']
        message = message.lower()
        good_stations = [station for station in SetMetroState.all_metro_stations
                         if station.lower().startswith(message)]
        if len(good_stations) == 0:
            return

        if len(good_stations) > config.max_inline_answers:
            good_stations = good_stations[:config.max_inline_answers]
        result = [BasicInlineResult(answer_id='station_{}_{}'.format(i, station),
                                    resulted_text=station,
                                    answer_title=station) for i, station in enumerate(good_stations)]
        answer = InlineAnswer(inline_query, result)
        answer.personal = True
        answer.cache_time = 5
        self.user.callback.answer_inline(answer)
