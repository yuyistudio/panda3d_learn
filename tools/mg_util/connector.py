# encoding: utf8

# 连接器,连接两片大陆

import random
import util
import grid
import sys
import math

class TwoCirclesConnectorGenerator(object):
    def __init__(self):
        pass

    def generate(self):
        #random.seed(1994)
        r1 = random.randint(3, 10)  # 圆圈半径
        r2 = random.randint(3, 10)
        bridge_length = random.randint(10, 20)  # 连接桥长度
        r = r1 + r2 + bridge_length  # 圆心距离
        angle = random.random() * math.pi * .5
        cx1, cy1 = r1 + 1, r1 + 1  # 圆的中心点
        cx2, cy2 = int(1 + cx1 + math.sin(angle) * r), int(1 + cy1 + math.cos(angle) * r)

        cells = grid.Grid(1000, 1000)
        cells.fill_circle(cx1, cy1, r1, 'x')
        cells.fill_circle(cx2, cy2, r2, 'o')
        cells.fill_line(cx1, cy1, cx2, cy2, 1, '+')
        cells.shrink()
        cells.print_self()


class FourCirclesConnectorGenerator(object):
    def __init__(self):
        pass

    def generate(self):
        seed = random.randint(0, 10)
        random.seed(seed)
        size = random.randint(60, 70)  # 地图的最大边长
        cell_size = size / 8  # 每个小格子的边长,差不多等于 size/10

        half_cell_size = cell_size / 2
        cells = grid.Grid(999, 999)
        points = [] # 记录圆圈中心点

        # 指定中心点,随机半径画圆
        def circle(sr, sc, radius=-1):
            if radius < 0:
                radius = random.randint(3, half_cell_size)
            cr = sr + random.randint(-half_cell_size, half_cell_size) * .5 + half_cell_size
            cc = sc + random.randint(-half_cell_size, half_cell_size) * .5 + half_cell_size
            cr = int(cr)
            cc = int(cc)
            points.append((cr, cc))
            cells.fill_circle(cr, cc, radius, 'o')

        # 最多画五个圆. 中间的圆必须画出来, 其他的不一定画出来
        circle(random.randint(cell_size, size-cell_size),
               random.randint(cell_size, size-cell_size),
               radius=5)
        centers = [
            (0, 0),
            (size - cell_size, size - cell_size),
            (0, size - cell_size),
            (size - cell_size, 0)]
        for center in centers:
            if random.random() < .7:
                circle(center[0], center[1])

        # 从中心点开始,向外画四条线
        for i in range(len(points) - 1):
            cells.fill_line(points[0][0], points[0][1], points[i+1][0], points[i+1][1], .7, '+')

        cells.shrink()
        cells.print_self()


class SimpleSquaresConnector(object):
    def generate(self):
        gap = 1
        sidewalk_size = 1
        count = random.randint(4, 6)
        r = 6
        c = 6
        cells = grid.Grid(888, 888)
        for i in range(count):
            size1 = random.randint(3, 6)
            size2 = random.randint(3, 6)
            cells.fill_rect(r-size1/2, c, r+size1/2, c+size2, 'x')
            if i < count - 1:
                cells.fill_line(r, c, r, c+size2 + gap, sidewalk_size, 'x')
            c += size2 + gap + 1
        cells.shrink()
        cells.print_self()



if __name__ == '__main__':
    SimpleSquaresConnector().generate()


