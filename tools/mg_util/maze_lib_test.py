# encoding: utf8

from mazelib.mazelib import *

m = Maze()
m.generator = Prims(50, 51)
m.solver = WallFollower()
print m.generate_monte_carlo(100, 10, 1.0)


