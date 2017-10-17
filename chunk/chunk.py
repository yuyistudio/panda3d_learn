#encoding: utf8


class Tile(object):
    def __init__(self):
        self._objects = []


class Chunk(object):
    """
    管理一堆Tiles和objects
    """
    def __init__(self, mgr, base_x, base_y, tile_count, tile_size):
        self._mgr, self._bx, self._by, self._tc, self._ts = \
            mgr, base_x, base_y, tile_count, tile_size

        self._tiles = []
        for i in range(tile_count * tile_count):
            self._tiles.append(Tile())
        self._frozen_objects = []

    def xy2rc(self, x, y):
        x -= self._bx
        y -= self._by
        return int(y / self._ts), int(x / self._ts)

    def rc2xy(self, r, c):
        return self._bx + c * self._ts, self._by + r * self._ts

    def rc_in_chunk(self, r, c):
        return 0 <= r < self._tc and 0 <= c < self._tc

