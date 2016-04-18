# -*- coding: utf-8 -*-
class WrongStateException(Exception):
    pass


class StateMetaClass(type):
    states = {}

    def __new__(cls, class_name, base_classes, param_dict):
        element = type.__new__(cls, class_name, base_classes, param_dict)
        if 'tag' not in param_dict or not isinstance(param_dict['tag'], str):
            raise WrongStateException
        tag = param_dict['tag']
        if tag != '':
            StateMetaClass.states[tag] = element
        return element
