#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
import ipdb
from collections import defaultdict

print("Start")
db = pymongo.MongoClient()['telegram_realty_bot_db']
db = db['flats']

print("Getting flats list")
flats = list(db.find({}, {'id': 1, 'comment': 1}))
print("Getting set")
flats.sort(key=lambda x: x['comment'])
good_fl = []

garbage = 0
current_comment = "aslkdhsdjkghsdlfk"
for flat in flats:
    comment = flat['comment']
    fid = flat['id']
    if comment != current_comment:
        current_comment = comment
        good_fl.append([fid])
    else:
        garbage += 1
        good_fl[-1].append(fid)

print(*(fl for fl in good_fl if len(fl) > 1), sep='\n')
print("Garbage count", garbage)
