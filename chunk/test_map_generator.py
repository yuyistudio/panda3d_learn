__author__ = 'Leon'

from util import random_util
import random


class TestMapGenerator(object):
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
                if random.random() < 0.05:
                    return {'object': {'name': 'box'}, 'title': self._tile}
                else:
                    return self._tpl
        assert False
