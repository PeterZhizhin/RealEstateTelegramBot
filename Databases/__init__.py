# -*- coding: utf-8 -*-
from pymongo import MongoClient, ASCENDING
import config


class Databases:
    mongo = MongoClient(host=config.mongo_url,
                        port=config.mongo_port,
                        connect=False)[config.mongo_database_name]
    mongo[config.users_db].create_index([('id', ASCENDING)], unique=True, name="user_id_index")

    mongo[config.user_links_db].create_index([('id', ASCENDING)], name="user_links_index")
    mongo[config.user_links_db].create_index([('next_update', ASCENDING)], name="update_index")

    mongo[config.flats_db].create_index([('id', ASCENDING)], unique=True, name="flat_id_index")

    @staticmethod
    def get_users_db():
        return Databases.mongo[config.users_db]

    @staticmethod
    def get_invites_db():
        return Databases.mongo[config.invites_db]

    @staticmethod
    def get_flats_db():
        return Databases.mongo[config.flats_db]

    @staticmethod
    def get_user_links_db():
        return Databases.mongo[config.user_links_db]
