# -*- coding: utf-8 -*-
import json


def dump_object(obj):
    return json.dumps(obj, separators=(',', ':'))


def load_object(obj_string):
    if isinstance(obj_string, bytes):
        obj_string = obj_string.decode('utf-8')
    return json.loads(obj_string)
