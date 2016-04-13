import logging
from . import User
from threading import Lock

logger = logging.getLogger("UserManager")


class UserManager:
    users_dict = dict()
    dict_lock = Lock()
    bot = None

    @staticmethod
    def set_bot(bot):
        UserManager.bot = bot

    @staticmethod
    def get_or_create_user(user_id):
        with UserManager.dict_lock:
            if user_id in UserManager.users_dict:
                return UserManager.users_dict[user_id]
            u = User(user_id, UserManager.bot.return_callback(user_id))
            logger.debug("Added user with ID " + str(user_id))
            UserManager.users_dict[user_id] = u
            return u
