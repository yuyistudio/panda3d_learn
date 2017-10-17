# encoding: utf8


"""
几个rc的概念：
    chunk_rc  chunk的世界坐标坐标
    world_rc  tile的世界坐标
    tile_rc   tile在chunk内的本地坐标
ChunkManager的rc函数使用chunk_rc.
Chunk的rc函数使用tile_rc.
"""

import chunk
from map_generator import DefaultRandomMapGenerator
import logging
import math


class DefaultObject(object):
    def __init__(self, name, x, y):
        self._name, self._x, self._y = name, x, y

    def get_pos(self):
        return self._x, self._y

    def get_name(self):
        return self._name

    def on_update(self, dt):
        pass

    def need_update(self):
        return True

    def on_unload(self):
        pass


class DefaultEntitySpawner(object):
    def spawn(self, x, y, config):
        return DefaultObject(config['name'], x, y)


class ChunkManager(object):
    def __init__(self, chunk_title_count=10, chunk_tile_size=1.):
        """
        :param chunk_title_count: chunk中的tile的数量
        :param chunk_tile_size: tile在世界中的尺寸
        :return:
        """
        self._chunk_tile_count = chunk_title_count
        self._chunk_tile_size = chunk_tile_size
        self._chunks = {}
        self._chunk_size = self._chunk_tile_count * self._chunk_tile_size  # chunk在世界中的尺寸
        self._center_chunk_id = (0, 0)
        self._generator = DefaultRandomMapGenerator()
        self._spawner = DefaultEntitySpawner()

    def set_spawner(self, spawner):
        self._spawner = spawner

    def set_generator(self, generator):
        self._generator = generator

    def __str__(self):
        items = []
        for chunk_id, chunk_data in self._chunks.iteritems():
            items.append(str(chunk_id))
        return "ChunkManager[%s]" % ('\t'.join(items))

    def get_chunk_ids(self):
        return self._chunks.keys()

    def xy2rc(self, x, y):
        c = int(math.floor(x / self._chunk_size))
        r = int(math.floor(y / self._chunk_size))
        return r, c

    def transfer_frozen_object(self, src_chunk, frozen_object):
        pos = frozen_object.get_pos()
        key = self.xy2rc(pos[0], pos[1])
        target_chunk = self._chunks.get(key)
        assert target_chunk != src_chunk, frozen_object.get_pos()
        if target_chunk:
            target_chunk.add_object(frozen_object)
            return True
        else:
            return False

    def rc2xy(self, r, c):
        return c * self._chunk_size, r * self._chunk_size

    @staticmethod
    def _iter_chunks(center_r, center_c):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                yield center_r + dr, center_c + dc

    def _load_chunk(self, r, c):
        bx, by = self.rc2xy(r, c)
        new_chunk = chunk.Chunk(self, bx, by, self._chunk_tile_count, self._chunk_tile_size)
        br = r * self._chunk_tile_count
        bc = c * self._chunk_tile_count
        for ir in range(br, br + self._chunk_tile_count):
            for ic in range(bc, bc + self._chunk_tile_count):
                ginfo = self._generator.get(ir, ic)
                obj_info = ginfo.get('object')
                if obj_info:
                    x = (ic + .5) * self._chunk_tile_size
                    y = (ir + .5) * self._chunk_tile_size
                    new_chunk.add_object(self._spawner.spawn(x, y, obj_info))
        return new_chunk

    def _unload_chunk(self, chunk_id):
        # 这里有个小坑，不能用 dict[key] = None 这种方式来删除key（在Lua中是可以的）。
        self._chunks[chunk_id].on_unload()
        del self._chunks[chunk_id]

    def on_update(self, x, y, dt):
        """
        根据位置进行更新，始终保持只有主角附近的chunk在内存中。
        :param x: 世界坐标x
        :param y: 世界坐标y
        :param dt: 单位秒
        :return: None
        """
        all_keys = set()
        r, c = self.xy2rc(x, y)
        self._center_chunk_id = (r, c)
        # 更新并创建不存在的chunk
        for (r, c) in self._iter_chunks(r, c):
            key = (r, c)
            all_keys.add(key)
            existing_chunk = self._chunks.get(key)
            if not existing_chunk:
                existing_chunk = self._load_chunk(r, c)
                self._chunks[key] = existing_chunk
            existing_chunk.on_update(dt)
        # 删除不在附近的chunk
        for chunk_id in self._chunks.keys():
            if chunk_id not in all_keys:
                self._unload_chunk(chunk_id)

import unittest


class ChunkManagerTest(unittest.TestCase):
    def test_rc2xy(self):
        cm = ChunkManager(2, 1)
        self.assertEqual(cm.rc2xy(1, 2), (4, 2))
        self.assertEqual(cm.xy2rc(3.2, 4.4), (2, 1))
        self.assertEqual(cm.rc2xy(-1, -2), (-4, -2))
        self.assertEqual(cm.xy2rc(-3.2, -4.4), (-3, -2))

        import random
        for i in range(32):
            r = int(random.random() * 1000)
            c = int(random.random() * 1000)
            cm.on_update(r, c, 0.5)
            self.assertEqual(len(set(cm.get_chunk_ids())), 9)

    def test_update_pos(self):
        cm = ChunkManager(10, 1)
        import random
        for i in range(100):
            cm.on_update((random.random() - .5) * 100, (random.random() - .5) * 100, 0.5)

    def test_update(self):
        cm = ChunkManager(10, 1)
        cm.on_update(1.5, 3.5, .02)
        expected_chunk_ids = (
            (1, -1), (1, 0), (1, 1),
            (0, -1), (0, 0), (0, 1),
            (-1, -1), (-1, 0), (-1, 1),
        )
        self.assertEqual(set(cm.get_chunk_ids()), set(expected_chunk_ids))

        cm.on_update(12.5, 9.5, .02)
        expected_chunk_ids = (
            (1, 0), (1, 1), (1, 2),
            (0, 0), (0, 1), (0, 2),
            (-1, 0), (-1, 1), (-1, 2),
        )
        self.assertEqual(set(cm.get_chunk_ids()), set(expected_chunk_ids))

        cm.on_update(44.5, 55.5, .02)
        expected_chunk_ids = (
            (6, 3), (6, 4), (6, 5),
            (5, 3), (5, 4), (5, 5),
            (4, 3), (4, 4), (4, 5),
        )
        self.assertEqual(set(cm.get_chunk_ids()), set(expected_chunk_ids))


if __name__ == '__main__':
    unittest.main()



