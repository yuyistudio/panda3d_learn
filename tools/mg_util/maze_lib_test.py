# encoding: utf8

from mazelib import mazelib
from mazelib.solve.WallFollower import WallFollower

from mazelib.generate.BacktrackingGenerator import BacktrackingGenerator
from mazelib.generate.BinaryTree import BinaryTree
from mazelib.generate.CellularAutomaton import CellularAutomaton
from mazelib.generate.Division import Division
from mazelib.generate.Ellers import Ellers
from mazelib.generate.GrowingTree import GrowingTree
from mazelib.generate.HuntAndKill import HuntAndKill
from mazelib.generate.Kruskal import Kruskal
from mazelib.generate.Perturbation import Perturbation
from mazelib.generate.Prims import Prims
from mazelib.generate.Sidewinder import Sidewinder
from mazelib.generate.TrivialMaze import TrivialMaze
from mazelib.generate.Wilsons import Wilsons


def gen_mazes():
    m = mazelib.Maze()
    generators = [BacktrackingGenerator, BinaryTree, CellularAutomaton, Division, Ellers, GrowingTree,
                  HuntAndKill, Kruskal, Prims, Sidewinder, TrivialMaze, Wilsons]

    m.solver = WallFollower()
    for generator in generators:
        print ('generating with %s' % generator)
        m.generator = generator(9, 9)
        try:
            maze_list = m.generate_monte_carlo(2, 2, 1.0)
        except RuntimeError, e:
            print('failed to solve %s' % generator)
            continue
        maze = maze_list[0]
        mazelib.print_grid(maze['grid'], maze['start'], maze['end'])


gen_mazes()