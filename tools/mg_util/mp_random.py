# encoding: utf8

import random


class RandomGenerator(object):
    def __init__(self):
        random.seed(0)

    def get(self, r, c):
        return random.choice(['wall', 'path', 'room'])


generator = RandomGenerator



