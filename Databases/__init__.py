from pymongo import MongoClient
import config


class Databases:
    mongo = MongoClient(host=config.mongo_url,
                        port=config.mongo_port)[config.mongo_database_name]

    @staticmethod
    def get_users_db():
        return Databases.mongo[config.users_db]

    @staticmethod
    def get_invites_db():
        return Databases.mongo[config.invites_db]

    @staticmethod
    def get_flats_db():
        return Databases.mongo[config.flats_db]
