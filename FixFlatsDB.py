# -*- coding: utf-8 -*-
from Databases import Databases

if __name__ == "__main__":
    db = Databases.get_flats_db()
    res_offers = [flat for flat in db.find({'location.metro.name': {'$exists': 1}},
                                           {'location.metro.name': 1, '_id': 1})]
    for offer in res_offers:
        metro_name = offer['location']['metro']['name']
        new_metro_name = metro_name.replace("м. ", "")
        print("Replacing {} with {}".format(metro_name, new_metro_name))
        db.update_one({'_id': offer['_id']}, {'$set': {'location.metro.name': new_metro_name}})
    db.update_many({}, {'$set': {'seen_by_suspicious_validator': False, 'suspicious': False}})
