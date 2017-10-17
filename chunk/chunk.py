#encoding: utf8


import math
import logging


class Tile(object):
    def __init__(self):
        self.objects = []


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

        self._update_iterator = self._iterate_objects()
        self._iterator_dt = 0

    def get_objects(self):
        objects = []
        for tile in self._tiles:
            objects.extend(tile.objects)
        return objects

    def add_object(self, obj):
        pos = obj.get_pos()
        r, c = self.xy2rc(pos[0], pos[1])
        assert self.rc_in_chunk(r, c), '%s , %s , %s,%s' % ((r, c), pos, self._bx, self._by)
        tile = self._tiles[r * self._tc + c]
        tile.objects.append(obj)

    def xy2rc(self, x, y):
        """
        :param x: 世界坐标x
        :param y:
        :return: Chunk内坐标r/c
        """
        x -= self._bx
        y -= self._by
        return int(math.floor(y / self._ts)), int(math.floor(x / self._ts))

    def rc2xy(self, r, c):
        """
        :param r: Chunk内坐标r/c
        :param c:
        :return: 世界坐标x/y
        """
        return self._bx + c * self._ts, self._by + r * self._ts

    def rc_in_chunk(self, r, c):
        """
        :param r: Chunk内坐标r/c
        :param c:
        :return:
        """
        return 0 <= r < self._tc and 0 <= c < self._tc

    def xy_in_chunk(self, x, y):
        """
        :param x: Chunk内坐标x/y
        :param y:
        :return:
        """
        r, c = self.xy2rc(x, y)
        return 0 <= r < self._tc and 0 <= c < self._tc

    def on_unload(self):
        for tile in self._tiles:
            for obj in tile.objects:
                obj.on_unload()

    def _iterate_objects(self):
        while True:
            for tile in self._tiles:
                remained_objects = []
                for obj in tile.objects:
                    obj.on_update(self._iterator_dt)
                    pos = obj.get_pos()
                    if self.xy_in_chunk(pos[0], pos[1]):
                        remained_objects.append(obj)
                    else:
                        self._frozen_objects.append(obj)
                    yield
                tile.objects = remained_objects

            remained_objects = []
            for frozen_obj in self._frozen_objects:
                if not self._mgr.transfer_frozen_object(self, frozen_obj):
                    remained_objects.append(frozen_obj)
            self._frozen_objects = remained_objects
            yield

    def on_update(self, dt):
        self._iterator_dt = dt
        self._update_iterator.next()
