# -*- coding: utf-8 -*-
import logging

from . import Databases
from datetime import datetime, timedelta
import time

logger = logging.getLogger("LinksDBManager")


class LinksDBManager:
    # Typical list entry:
    # {'id': <USER ID>, 'url': <URL>, 'tag': <TAG>,
    # 'frequency': <TIME in secs>,
    # 'last_update': <Timestamp>
    # 'next_update': <Timestamp>,
    # 'type': <"CIAN", "Yandex", "Avito", etc.>}
    links_db = Databases.get_user_links_db()
    if links_db.count() > 0:
        next_estimated_link_update = min(update['next_update'] for update in links_db.find())
    else:
        next_estimated_link_update = datetime.utcnow()

    @staticmethod
    def get_left_time_before_new_link_arrival():
        now = datetime.utcnow()
        if LinksDBManager.links_db.count() == 0:
            LinksDBManager.next_estimated_link_update = datetime.utcnow() + timedelta(seconds=10)
            return 10
        if LinksDBManager.next_estimated_link_update > now:
            return (LinksDBManager.next_estimated_link_update - now).seconds
        return 0

    @staticmethod
    def get_user_links(user_id):
        return LinksDBManager.links_db.find({'id': user_id})

    @staticmethod
    def add_user_link(user_id, url, tag, frequency, link_type):
        res = LinksDBManager.links_db.insert_one({'id': user_id,
                                                  'url': url,
                                                  'tag': tag,
                                                  'frequency': frequency,
                                                  'last_update': datetime.utcnow(),
                                                  'next_update': datetime.utcnow() + timedelta(minutes=frequency),
                                                  'type': link_type})
        return LinksDBManager.links_db.find_one({'_id': res.inserted_id})

    @staticmethod
    def remove_all_links(user_id):
        LinksDBManager.links_db.delete_many({'id': user_id})

    @staticmethod
    def update_frequency(unique_id, new_frequency):
        next_update = LinksDBManager.links_db.find_one({"_id": unique_id})['last_update'] + \
                      timedelta(minutes=new_frequency)
        return LinksDBManager.links_db.update_one({"_id": unique_id}, {"$set": {"frequency": new_frequency,
                                                                                "next_update": next_update}})

    @staticmethod
    def get_expired_links():
        if datetime.utcnow() >= LinksDBManager.next_estimated_link_update:
            logger.debug("Querying database for new links")
            LinksDBManager.next_estimated_link_update = None
            for update in list(LinksDBManager.links_db.find({'next_update': {"$lte": datetime.utcnow()}})):
                LinksDBManager.update_expiration_time(update['_id'])
                yield update
            if LinksDBManager.next_estimated_link_update is None:
                LinksDBManager.next_estimated_link_update = datetime.utcnow()
        else:
            return []

    @staticmethod
    def update_expiration_time(unique_id):
        update = LinksDBManager.links_db.find_one({"_id": unique_id})
        now_time = datetime.utcnow()
        next_time = datetime.utcnow() + timedelta(minutes=update['frequency'])
        if LinksDBManager.next_estimated_link_update is None \
                or LinksDBManager.next_estimated_link_update > next_time:
            LinksDBManager.next_estimated_link_update = next_time
        return LinksDBManager.links_db.update_one({"_id": unique_id},
                                                  {"$set": {
                                                      'last_update': now_time,
                                                      "next_update": next_time,
                                                  }})
