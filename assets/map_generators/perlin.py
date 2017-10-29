# encoding: utf8

__author__ = 'Leon'

import random
from util import random_util
import sys
from panda3d.core import Vec3


class PerlinMapGenerator(object):
    def __init__(self, debug=False):
        self._mapping = [
            (.3, 'grass1'),
            (.5, 'grass2'),
            (.6, 'rock2'),
            (.65, 'plate'),
            (.7, 'floor1'),
            (.74, 'floor2'),
            (1.01, 'barren'),
        ]
        if debug:
            self._mapping = [(.4, '@'), (.7, '.'), (.8, '+'), (1.01, 'O')]

        self._tile = {'name': 'UNSET'}
        self._tpl = {'tile': self._tile}
        self._obj_tpl = {'tile': self._tile, 'object': None}

    def get(self, r, c):
        v = random_util.perlin_noise_2d(r, c, 0.13)
        for item in self._mapping:
            threshold, tile_type = item[0], item[1]
            if v < threshold:
                self._tile['name'] = tile_type
                if 'grass' in tile_type and False:
                    rand_v = random.random()
                    if rand_v < .02:
                        self._obj_tpl['object'] = {'name': 'tree'}
                    elif rand_v < .103:
                        self._obj_tpl['object'] = {'name': 'twig'}
                    else:
                        return self._tpl
                    return self._obj_tpl
                else:
                    return self._tpl
        assert False


def test_perlin_generator():
    pg = PerlinMapGenerator(debug=True)
    br, bc = 100, 100
    for i in range(40):
        for j in range(40):
            sys.stdout.write('  ' + pg.get(br + i, bc + j)['tile']['name'])
        sys.stdout.write('\n')

