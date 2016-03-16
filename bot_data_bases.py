from pymongo import MongoClient
import config
mongo = None
def open_db():
    global mongo
    if mongo is None:
        mongo = MongoClient(host=config.mongo_url, port=config.mongo_port)
        mongo = mongo[config.mongo_database_name]

def get_users_db():
    open_db()
    return mongo[config.users_db]

def get_invites_db():
    open_db()
    return mongo[config.invites_db]

def get_flats_db():
    open_db()
    return mongo[config.flats_db]
