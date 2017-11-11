# encoding: utf8

import grid

INVALID = None
WALL = 'wall'
PATH = 'path'

class RandomDigger(object):
    def __init__(self):
        self._data = grid.Grid(50, 50)
        self._sr = 25
        self._sc = 25

    def get(self, r, c):
        return self._data.get(r, c)

    def get_start_pos(self):
        return self._sr, self._sc

    def _dig_around(self, r, c, dr, dc):
        pass

    def _generate(self):
        r = self._sr
        c = self._sc


