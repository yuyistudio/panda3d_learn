# encoding: utf8

import random
import math


class Generator(object):
    def __init__(self):
        random.seed(0)

    def get(self, r, c):
        dist = math.sqrt((r - 25)**2 + (c - 25)**2)
        if dist < 10:
            return 'wall'
        elif dist < 15:
            return 'path'
        elif dist < 20:
            return 'room'
        else:
            return None

generator = Generator



