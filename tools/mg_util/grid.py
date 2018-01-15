# encoding: utf8

import sys
import math

class Grid(object):
    def __init__(self, rows, cols):
        self._rows = rows
        self._cols = cols
        self._data = self._create_data(rows, cols)

    def _create_data(self, rows, cols, value=0):
        data = []
        for r in range(rows):
            data.append([value] * cols)
        return data

    def rows(self):
        return self._rows

    def cols(self):
        return self._cols

    def is_in_range(self, r, c):
        if r < 0 or c < 0 or r >= self._rows or c >= self._cols:
            return False
        return True

    def get(self, r, c):
        if r < 0 or c < 0 or r >= self._rows or c >= self._cols:
            return None
        return self._data[r][c]

    def get_unsafe(self, r, c):
        return self._data[r][c]

    def set(self, r, c, data):
        if r < 0 or c < 0 or r >= self._rows or c >= self._cols:
            return None
        self._data[r][c] = data

    def set_unsafe(self, r, c, data):
        self._data[r][c] = data

    def is_all_eq(self, r, c, w, h, target):
        start_r = max(r, 0)
        start_c = max(c, 0)
        end_r = min(r + h, self._rows)
        end_c = min(r + w, self._cols)
        if end_r <= start_r or end_c <= start_c:
            return False
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                if self._data[r][c] != target:
                    return False
        return True

    # 闭区间
    def fill_rect(self, r1, c1, r2, c2, data):
        sr, er, sc, ec = min(r1, r2), max(r1, r2), min(c1, c2), max(c1, c2)
        self.set_all(sr, sc, ec - sc + 1, er - sr + 1, data)

    def fill_circle(self, cr, cc, radius, data):
        r1, r2 = cr - radius, cr + radius
        c1, c2 = cc - radius, cc + radius
        r1 = min(max(r1, 0), self._rows-1)
        r2 = min(max(r2, 0), self._rows-1)
        c1 = min(max(c1, 0), self._cols-1)
        c2 = min(max(c2, 0), self._cols-1)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if (r - cr)**2+(c-cc)**2 <= radius**2:
                    self._data[r][c] = data

    def fill_line(self, r1, c1, r2, c2, width, data):
        # 直线参数
        A = r2 - r1
        B = c1 - c2
        C = c2*r1-c1*r2
        S = math.sqrt(A**2+B**2)
        if S == 0:
            raise RuntimeError("!!")
        sr, er, sc, ec = min(r1, r2), max(r1, r2), min(c1, c2), max(c1, c2)
        for r in range(sr, er+1):
            for c in range(sc, ec+1):
                dist = math.fabs(A * c + B * r + C) / S
                if dist < width:
                    self._data[r][c] = data

    def set_all(self, r, c, w, h, data):
        start_r = max(r, 0)
        start_c = max(c, 0)
        end_r = min(r + h, self._rows)
        end_c = min(c + w, self._cols)
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                self._data[r][c] = data

    # 删除不用的方块,减少rows/cols
    def shrink(self):
        min_r, min_c, max_r, max_c = self._rows, self._cols, 0, 0
        for r in range(self._rows):
            for c in range(self._cols):
                if not self._data[r][c]:
                    continue
                if r < min_r:
                    min_r = r
                if r > max_r:
                    max_r = r
                if c < min_c:
                    min_c = c
                if c > max_c:
                    max_c = c
        if min_r > max_r:
            raise RuntimeError(' '.join([str(v) for v in ('invalid:', min_r, min_c, max_r, max_c)]))

        rows = max_r - min_r + 1
        cols = max_c - min_c + 1
        print 'after shrink size:', rows, cols, 'min/max:', (min_r, min_c, max_r, max_c)
        data = self._create_data(rows, cols)
        for r in range(min_r, min_r + rows):
            for c in range(min_c, min_c + cols):
                data[r-min_r][c-min_c] = self._data[r][c]
        self._data = data
        self._rows = rows
        self._cols = cols

    def print_self(self):
        for i in range(self._rows):
            for j in range(self._cols):
                data = self._data[i][j]
                if not data:
                    sys.stdout.write('  ')
                else:
                    sys.stdout.write('%s ' % data)
            sys.stdout.write('\n')
        sys.stdout.write('\n')

if __name__ == '__main__':
    g = Grid(4, 4)
    g.set(1, 1, 'x')
    g.set(3, 2, 'y')
    g.print_self()
    g.shrink()
    g.print_self()



