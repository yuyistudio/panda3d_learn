# encoding: utf8

import random
import math


class Generator(object):
    def __init__(self):
        self._center_r = 25
        self._center_c = 25
        random.seed(0)
    
    def get_start_pos(self):
        return self._center_r, self._center_c

    def get(self, r, c):
        dist = math.sqrt((r - self._center_r)**2 + (c - self._center_c)**2)
        if dist < 10:
            return 'wall'
        elif dist < 15:
            return 'path'
        elif dist < 20:
            return 'room'
        else:
            return None

generator = Generator



