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

