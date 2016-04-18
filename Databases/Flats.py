# -*- coding: utf-8 -*-
from . import Databases


class FlatsDB:
    db = Databases.get_flats_db()

    @staticmethod
    def get_flat(flat_id):
        return FlatsDB.db.find_one({"id": flat_id})
