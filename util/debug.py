# encoding: utf8

__author__ = 'Leon'


from variable.global_vars import G

_keys = set()


def add_debug_key(key, fn, args=[]):
    if key in _keys:
        assert False, key
    _keys.add(key)
    G.accept(key, fn, args)
