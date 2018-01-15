# encoding: utf8

import random
import sys

DIRS = ['east', 'west', 'north', 'south']
DIR2OFFSET = {
    'east': (0, 1),
    'west': (0, -1),
    'north': (1, 0),
    'south': (-1, 0),
}


def random_dir_offset():
    return DIR2OFFSET[random.choice(DIRS)]


def int_str(n, digits):
    res = str(n)
    if len(res) < digits:
        pad = '0' * (digits - len(res))
        return pad + res
    return res

