# encoding: utf8

__author__ = 'Leon'

import random
from util import random_util
import sys
from panda3d.core import Vec3


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


class PerlinMapGenerator(object):
    def __init__(self, debug=False):
        self._mapping = [(.2, 'desert'), (.5, 'grass'), (.7, 'rock'), (1.01, 'forest')]
        if debug:
            self._mapping = [(.4, '@'), (.7, '.'), (.8, '+'), (1.01, 'O')]

        self._tile = {'name': 'UNSET'}
        self._tpl = {'tile': self._tile}

    def get(self, r, c):
        v = random_util.perlin_noise_2d(r, c, 0.13)
        for item in self._mapping:
            threshold, tile_type = item[0], item[1]
            if v < threshold:
                self._tile['name'] = tile_type
                return self._tpl
        assert False


def test_perlin_generator():
    pg = PerlinMapGenerator(debug=True)
    br, bc = 100, 100
    for i in range(40):
        for j in range(40):
            sys.stdout.write('  ' + pg.get(br + i, bc + j)['tile']['name'])
        sys.stdout.write('\n')


class DefaultObject(object):
    def __init__(self, name, x, y):
        self._name, self._x, self._y = name, x, y

    def get_pos(self):
        return Vec3(self._x, self._y, 0)

    def get_name(self):
        return self._name

    def on_update(self, dt):
        pass

    def need_update(self):
        return True

    def on_unload(self):
        pass

    def on_save(self):
        pass

    def on_destroy(self):
        pass


class DefaultEntitySpawner(object):
    def spawn(self, x, y, config):
        return DefaultObject(config['name'], x, y)

