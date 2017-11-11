# encoding: utf8


class Grid(object):
    def __init__(self, rows, cols):
        self._rows = rows
        self._cols = cols
        self._data = [[0] * cols] * rows

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

    def set_all(self, r, c, w, h, target):
        start_r = max(r, 0)
        start_c = max(c, 0)
        end_r = min(r + h, self._rows)
        end_c = min(r + w, self._cols)
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                if self._data[r][c] != target:
                    return False
        return True
