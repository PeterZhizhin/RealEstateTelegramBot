from pymongo import MongoClient
import config


class Databases:
    mongo = None

    @staticmethod
    def open_db():
        if Databases.mongo is None:
            Databases.mongo = MongoClient(host=config.mongo_url, port=config.mongo_port)
            Databases.mongo = Databases.mongo[config.mongo_database_name]

    @staticmethod
    def get_users_db():
        Databases.open_db()
        return Databases.mongo[config.users_db]

    @staticmethod
    def get_invites_db():
        Databases.open_db()
        return Databases.mongo[config.invites_db]

    @staticmethod
    def get_flats_db():
        Databases.open_db()
        return Databases.mongo[config.flats_db]
