# encoding: utf8

# 房间列表.每个房间放到固定大小的cell中进行缩放,房间保证从起点可达.

import random
import util
import grid
import sys
from maze_generator.maze import Maze


class SimpleMazeGenerator(object):
    def generate(self):
        random.seed(1)
        maze = Maze(20, 20, 1)
        gap = 2
        grid, entry, exit, path_gen = maze.generate_maze((0, 0))
        cells = []
        for r in range(maze.num_rows):
            rows = []
            for i in range(gap):
                rows.append([])
            for c in range(maze.num_cols):
                walls = grid[r][c].walls
                rows[0].append('o')
                for i in range(gap-1):
                    rows[0].append(' ' if walls['right'] else 'o')
                for i in range(gap-1):
                    rows[i+1].append(' ' if walls['bottom'] else 'o')
                for i in range(gap-1):
                    for j in range(gap-1):
                        rows[i+1].append(' ')
            for row in rows:
                cells.append(row)
        cells[entry[0]*gap][entry[1]*gap] = '@'
        cells[exit[0]*gap][exit[1]*gap] = 'X'
        for r in range(maze.num_rows*gap):
            for c in range(maze.num_cols*gap):
                sys.stdout.write('%s ' % cells[r][c])
            sys.stdout.write('\n')

if __name__ == '__main__':
    SimpleMazeGenerator().generate()


