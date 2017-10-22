#encoding: utf8


import math
import logging
from panda3d.core import Vec3
from variable.global_vars import G
import sys


class Tile(object):
    def __init__(self, r, c):
        self.objects = []
        self.r, self.c = r, c


class Chunk(object):
    """
    管理一堆Tiles和objects
    """
    def __init__(self, mgr, base_x, base_y, tile_count, tile_size):
        self._mgr, self._bx, self._by, self._tc, self._ts = \
            mgr, base_x, base_y, tile_count, tile_size

        r, c = self.xy2rc(base_x, base_y)
        self._tiles = []
        for i in range(tile_count):
            for j in range(tile_count):
                self._tiles.append(Tile(r + i, c + j))
        self._frozen_objects = []

        self._update_iterator = self._iterate_objects()
        self._iterator_dt = 0
        self._enabled = True
        self._ground_geom = None
        self._ground_data = None

    def set_ground_geom(self, geom, data):
        self._ground_geom = geom
        self._ground_data = data

    def get_ground_data(self):
        return self._ground_data

    def get_objects(self):
        objects = []
        for tile in self._tiles:
            objects.extend(tile.objects)
        return objects

    def get_tile_at(self, r, c):
        tile = self._tiles[r * self._tc + c]
        assert tile, 'rc (%s,%s) not in chunk range' % (r, c)
        return tile

    def add_object_to(self, obj, r, c):
        tile = self._tiles[r * self._tc + c]
        assert tile, 'rc (%s,%s) not in chunk range' % (r, c)
        tile.objects.append(obj)

    def add_object(self, obj):
        pos = obj.get_pos()
        r, c = self.xy2rc(pos.getX(), pos.getY())
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

    def on_load(self, spawner, data):
        self._ground_data = data['ground']
        for obj_data in data['objects']:
            obj = spawner.spawn_from_storage(obj_data)
            assert obj, 'invalid storage data: %s' % obj_data
            self.add_object(obj)

    def on_unload(self):
        objects_data = []
        for tile in self._tiles:
            for obj in tile.objects:
                objects_data.append(obj.on_save())
                obj.on_destroy()
        for obj in self._frozen_objects:
            objects_data.append(obj.on_save())
            obj.on_destroy()
        return {
            'objects': objects_data,
            'ground': self._ground_data,
        }

    def _iterate_objects(self):
        while True:
            # 每一帧更新一个Tile
            for tile in self._tiles:
                obj = None
                remained_objects = []
                for obj in tile.objects:
                    obj.on_update(self._iterator_dt)
                    pos = obj.get_pos()
                    if self.xy_in_chunk(pos.getX(), pos.getY()):
                        remained_objects.append(obj)
                    else:
                        self._frozen_objects.append(obj)
                tile.objects = remained_objects
                del obj  # 每一帧中都确保没有对entity的多余引用
                yield

            # 更新所有的frozen_objects
            remained_objects = []
            frozen_obj = None
            for frozen_obj in self._frozen_objects:
                if not self._mgr.transfer_frozen_object(self, frozen_obj):
                    remained_objects.append(frozen_obj)
            self._frozen_objects = remained_objects
            del frozen_obj  # 每一帧中都确保没有对entity的多余引用
            yield

    def on_update(self, dt):
        if not self._enabled:
            return
        self._iterator_dt = dt
        self._update_iterator.next()

    def set_enabled(self, enabled):
        self._enabled = enabled
        if self._ground_geom:
            if enabled:
                self._ground_geom.reparent_to(G.render)
            else:
                self._ground_geom.detach_node()
        for obj in self._iter_all_objects():
            obj.set_enabled(enabled)

    def _iter_all_objects(self):
        """
        遍历该chunk内的所有object。包括frozen_objects。
        :return:
        """
        for tile in self._tiles:
            for obj in tile.objects:
                yield obj
        for obj in self._frozen_objects:
            yield obj

    def clear_objects(self):
        for obj in self._frozen_objects:
            # 为什么是3：1、局部变量obj；2、self._frozen_objects；3、getrefcount(obj)的参数；
            assert sys.getrefcount(obj) == 3
        del self._frozen_objects[:]
        for tile in self._tiles:
            if tile.objects:
                assert sys.getrefcount(tile.objects[0]) == 2, \
                    'unexpected ref count: %d, obj: %s' % (sys.getrefcount(tile.objects[0]), tile.objects[0])
                del tile.objects[:]

