# -*- coding: utf-8 -*-
import logging
import threading
import time
from datetime import datetime

import string

import math

import config
import pytz
from Databases import Databases

logger = logging.getLogger("Suspicious checker")


class SuspiciousChecker:
    thread = None
    need_close = None
    zone = pytz.timezone("Europe/Moscow")
    last_check_date = None

    @staticmethod
    def time_is_right():
        now = datetime.now(SuspiciousChecker.zone)
        # return 3 <= now.hour <= 5
        is_right_day = now.isoweekday() == config.suspicious_check_weekday_iso
        is_right_time = config.suspicious_check_hour_min <= now.hour < config.suspicious_check_hour_max
        if is_right_day and is_right_time:
            if SuspiciousChecker.last_check_date is None \
                    or SuspiciousChecker.last_check_date != now.date():
                SuspiciousChecker.last_check_date = now.date()
                return True
            return False
        return False

    @staticmethod
    def safe_sleep(seconds):
        left = seconds
        while not SuspiciousChecker.need_close and left > 0:
            left -= 1
            time.sleep(1)

    @staticmethod
    def fix_price(flat):
        price = flat['price'][0]
        price = "".join(c for c in price if c in string.digits)
        return int(price)

    @staticmethod
    def check_suspicious():
        logger.info("Checking suspicious")
        db = Databases.get_flats_db()
        logger.debug("Getting target flats")
        target_flats = list(db.find({'seen_by_suspicious_validator': False,
                                     'location.metro': {'$exists': True}},
                                    {'id': 1,
                                     'price': 1,
                                     'location.metro.name': 1}))
        logger.debug("Got {}".format(len(target_flats)))
        for flat in target_flats:
            flat['price'] = SuspiciousChecker.fix_price(flat)
            flat['metro'] = flat['location']['metro']['name']
            del flat['location']
        logger.debug("Fixed names")
        suspicious_flats = []
        stations = set(flat['metro'].lower() for flat in target_flats)
        logger.debug("Getting suspicious flats")
        for station in stations:
            station_flats = [flat for flat in target_flats if flat['metro'].lower() == station]
            suspicious_num = math.ceil(len(station_flats) * config.suspicious_fraction)
            station_flats.sort(key=lambda x: x['price'])
            suspicious_flats.extend(station_flats[:suspicious_num])

        target_flats_ids = [flat['id'] for flat in target_flats]
        suspicious_flats_ids = [flat['id'] for flat in suspicious_flats]
        logger.debug("Pushing to DB")
        db.update_many({'id': {'$in': target_flats_ids}}, {'$set': {'seen_by_suspicious_validator': True}})
        db.update_many({'id': {'$in': suspicious_flats_ids}}, {'$set': {'suspicious': True}})

    @staticmethod
    def work():
        while not SuspiciousChecker.need_close:
            if SuspiciousChecker.time_is_right():
                SuspiciousChecker.check_suspicious()
            SuspiciousChecker.safe_sleep(config.suspicious_check_sleep_time)

    @staticmethod
    def register():
        SuspiciousChecker.thread = threading.Thread(target=SuspiciousChecker.work)
        SuspiciousChecker.thread.start()

    @staticmethod
    def close_thread():
        SuspiciousChecker.need_close = True
        SuspiciousChecker.thread.join()
