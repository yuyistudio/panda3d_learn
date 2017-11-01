# encoding: utf8

__author__ = 'Leon'


class LRUCache(object):
    """
    保留最近添加的Max_count个object
    """
    def __init__(self, max_count=6):
        self._keys = []
        self._hash = {}
        self._max_keys = max_count

    def debug_peek(self, key):
        return self._hash.get(key)

    def add(self, key, value):
        """
        添加一个kvpair，返回一个过期的kvpair。
        :param key:
        :param value:
        :return:
        """
        assert key not in self._hash
        trash_key = None
        trash_value = None
        if len(self._keys) == self._max_keys:
            trash_key = self._keys[0]
            trash_value = self._hash[trash_key]
            self._keys.pop(0)
            del self._hash[trash_key]
        self._keys.append(key)
        self._hash[key] = value
        return trash_key, trash_value

    def get(self, key):
        """
        Get and remove.
        :param key:
        :return:
        """
        try:
            idx = self._keys.index(key)
        except:
            return None
        self._keys.pop(idx)
        v = self._hash[key]
        del self._hash[key]
        return v

