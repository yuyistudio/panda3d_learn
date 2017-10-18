# encoding: utf8

__author__ = 'Leon'

import random


class DefaultRandomMapGenerator(object):
    def __init__(self):
        self._rand = random.Random()
        self._rand.seed(19930928)

    def get(self, r, c):
        if self._rand.random() < 0.3:
            return {
                'object': {
                    'name': 'box',
                },
                'tile': {
                    'name': 'dirt',
                }
            }
        else:
            return {
                'tile': {
                    'name': 'dirt',
                }
            }


class TilesOnlyMapGenerator(object):
    def get(self, r, c):
        return {
            'tile': {
                'name': 'dirt',
            }
        }


class DefaultObject(object):
    def __init__(self, name, x, y):
        self._name, self._x, self._y = name, x, y

    def get_pos(self):
        return self._x, self._y

    def get_name(self):
        return self._name

    def on_update(self, dt):
        pass

    def need_update(self):
        return True

    def on_unload(self):
        pass


class DefaultEntitySpawner(object):
    def spawn(self, x, y, config):
        return DefaultObject(config['name'], x, y)

