from . import Databases
from datetime import datetime, timedelta


class LinksDBManager:
    # Typical list entry:
    # {'id': <USER ID>, 'url': <URL>, 'tag': <TAG>,
    # 'frequency': <TIME in secs>,
    # 'last_update': <Timestamp>
    # 'next_update': <Timestamp>,
    # 'type': <"CIAN", "Yandex", "Avito", etc.>}
    links_db = Databases.get_user_links_db()

    @staticmethod
    def get_user_links(user_id):
        return LinksDBManager.links_db.find({'id': user_id})

    @staticmethod
    def add_user_link(user_id, url, tag, frequency, link_type):
        return LinksDBManager.links_db.insert_one({'id': user_id,
                                                   'url': url,
                                                   'tag': tag,
                                                   'frequency': frequency,
                                                   'last_update': datetime.now(),
                                                   'next_update': datetime.now() + timedelta(minutes=frequency),
                                                   'type': link_type})

    @staticmethod
    def update_frequency(unique_id, new_frequency):
        next_update = LinksDBManager.links_db.find_one({"_id": unique_id})['last_update'] + \
                      timedelta(minutes=new_frequency)
        return LinksDBManager.links_db.update_one({"_id": unique_id}, {"$set": {"frequency": new_frequency,
                                                                                "next_update": next_update}})

    @staticmethod
    def get_expired_links():
        return LinksDBManager.links_db.find({'next_update': {"$lte": datetime.now()}})

    @staticmethod
    def update_expiration_time(unique_id):
        update = LinksDBManager.links_db.find_one({"_id": unique_id})
        return LinksDBManager.links_db.update_one({"_id": unique_id},
                                                  {"$set": {
                                                      'last_update': datetime.now(),
                                                      "next_update": datetime.now() +
                                                                     timedelta(minutes=update['frequency'])
                                                  }})
