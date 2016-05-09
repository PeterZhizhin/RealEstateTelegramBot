# -*- coding: utf-8 -*-
import re

# User
# None state
hello_message = "Добро пожаловать в бот аренды. Для продолжения введите инвайт."
auth_failed = "Авторизация провалена. Инвайт неверен. Осталось попыток: "
auth_finished = "Авторизация успешна."
auth_totally_failed = "Авторизация запрещена. Не осталось попыток."
start_id = '/start'

# Main state
main_help = """Добро пожаловать в бот аренды квартир.
Доступны следующие команды:
/help Напечатать это сообщение.
/add_link Добавить ссылку.
/get_links Получить список текущих ссылок.
/set_updates Установить частоту обновлений по ссылкам.
/set_max_price Установить максимальную цену (не влияет на предложения по ссылкам).
/set_stations Установить станции метро (не влияет на предложения по ссылкам)."""
wrong_command = "Неверная команда. Наберите /help для помощи."
help_id = '/help'
add_link_id = '/add_link'
get_links_id = '/get_links'
set_updates_id = '/set_updates'
set_price_id = '/set_max_price'
set_stations_id = '/set_stations'

# Admin only
invoke_invites = '/invites_invoke'
admin_hello = "Hello, admin!"
invoke_invite_inline_msg = 'Сгенерировать инвайт'

current_links_message = "Список текущих ссылок:"
no_links_message = "Ссылок нет."

awaitance_time_exceeded = "Превышено время ожидания. Повторите попытку."
cancel_id = '/cancel'

add_link_enter = "Введите ссылку или /cancel для отмены"
add_link_failed = "Добавление ссылки \"{tag}\" не удалось. Попробуйте ещё раз, набрав /add_link"
add_link_success = "Добавление ссылки \"{tag}\" успешно."

add_link_tag_enter = "Введите метку для ссылки. Например: \"1 комната в центре до 30к\" (максимум 30 символов)."
add_link_tag_wrong_tag = "Метка неверна. Проверьте её длину. Для отмены введите /cancel."
add_link_queue_notification = "Мы проверим ссылку, а вам вскоре вам придет уведомление о результате."
updates_time_not_setted_up = "Частота обновлений задана по умолчанию (60 минут)." \
                             "Вы можете изменить её при помощи команды /set_updates."

set_updates_enter_message = "Введите время (в минутах) о том, как часто" \
                            " бы вы хотели получать уведомления о новых квартирах" \
                            " (минимум 60 минут). /cancel для отмены"
set_updates_wrong_time_str = "Кажется, это не время в минутах (введите число). Попробуйте ещё раз." \
                             " /cancel для отмены"
set_updates_wrong_duration = "Минимумальное время между обновлениями -- это 60 минут. Попробуйте ещё раз." \
                             " /cancel для отмены."
set_updates_success = "Частота обновлений успешна установлена."

set_price_enter_message = "Введите максимальную цену в рублях. /cancel для отмены."
set_price_wrong_price = "Кажется, это не цена. Введите число. /cancel для отмены."
set_price_success = "Максимальная цена установлена"

station_names = sorted([
    # Green line
    "Речной вокзал",
    "Водный стадион",
    "Войковская",
    "Сокол",
    "Аэропорт",
    "Динамо",
    "Белорусская",

    # Purple
    "Краснопресненская",
    "Баррикадная",
    "Улица 1905 года",
    "Беговая",
    "Полежаевская",
    "Октябрьское Поле",
    "Щукинская",
    "Спартак",
    "Тушинская",
    "Сходненская",
    "Планерная",

    # Light blue line
    "Киевская",
    "Студенческая",
    "Кутузовская",
    "Фили",
    "Багратионовская",
    "Филевский парк",
    "Пионерская",
    "Кунцевская",
    "Выставочная",
    "Международная",

    # Blue line
    "Пятницкое шоссе",
    "Митино",
    "Волоколамская",
    "Мякинино",
    "Строгино",
    "Крылатское",
    "Молодежная",
    "Кунцевская",
    "Славянский бульвар",
    "Парк Победы",

    # Moscow city
    "Деловой центр",
])
stop_id = "/stop"
clear_stations_id = "/clear_stations"
set_stations_enter = "Чтобы добавить или удалить станцию воспользуйтесь inline.\n" \
                     "Например: @the_realty_bot Аэропорт.\n" \
                     "Чтобы удалить все станции - наберите /clear_stations\n" \
                     "Когда закончите -- введите /stop\n" \
                     "К сожалению, пока доступны только квартиры на северо-западе Москвы " \
                     "на расстоянии 15 минут ходьбы от метро.\n" \
                     "Если вам нужны другие квартиры - вы можете установить ссылку в главном меню."
clear_stations_message = "Станции удалены. Если вы закончили - наберите /stop"
current_stations_base = "Список текущих станций: {}\n" \
                        "Если вы закончили - наберите /stop"
deleted_last_station = "Последняя станция удалена. Наберите /stop чтобы закончить."
station_added_message = "Станция {} добавлена."
station_deleted_message = "Станция удалена."
station_not_found_message = "Станция {} не найдена. Попробуйте ещё раз. /stop"

base_for_sending_flat = """Адрес:
Метро: {metro}
Адрес: {address}

Информация:
Объект: {object}
Площади: {sizes_total}
Этаж: {floor}

Цена:
{price} ({price_info})
Процент: {percent}

Дополнительные сведения:
{additional_info}

Комментарий:
{comment}

Контакты:
{contacts}
"""
go_to_flat_by_url_caption = "Открыть в браузере"
base_for_sending_preview = "{location} {price} {info_cmd}"
cian_base_cmd = "/cian{id}"
cian_cmd_regexp = re.compile("\/cian([0-9]+)")

no_flat_with_id = "Квартиры с таким id не найдено"

