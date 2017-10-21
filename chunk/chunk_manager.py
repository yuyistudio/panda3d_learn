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
from map_generator import *
import math


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
        """
        :param spawner:
            get(x, y, config)
        :return:
        """
        self._spawner = spawner

    def set_generator(self, generator):
        """
        :param generator:
            get(r,c)
                return {
                    'tile':{'name':'xx'},
                    'object':{'name':'xx'}
                }
        :return:
        """
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
        # assert target_chunk != src_chunk, frozen_object.get_pos()
        if target_chunk:
            target_chunk.add_object(frozen_object)
            return True
        else:
            return False

    def rc2xy(self, r, c):
        return c * self._chunk_size, r * self._chunk_size

    @staticmethod
    def _iter_chunk_keys(center_r, center_c):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                yield center_r + dr, center_c + dc

    def xy2world_rc(self, x, y):
        c = int(math.floor(x / self._chunk_tile_size))
        r = int(math.floor(y / self._chunk_tile_size))
        return r, c

    def world_rc2chunk_rc(self, r, c):
        return r / self._chunk_tile_count, c / self._chunk_tile_count

    def world_rc2inner_rc(self, r, c):
        return r / self._chunk_tile_count, c / self._chunk_tile_count

    def get_around_tiles(self, x, y, radius):
        """
        Warning 该函数性能较差, 不适合经常调用
        :param x:
        :param y:
        :param radius:
        :return:
        """
        world_r, world_c = self.xy2world_rc(x, y)
        tiles = []
        for delta_r in range(-radius, radius + 1):
            for delta_c in range(-radius, radius + 1):
                key = self.world_rc2chunk_rc(world_r + delta_r, world_c + delta_c)
                chk = self._chunks.get(key)
                if not chk:
                    continue
                inner_r, inner_c = world_r + delta_r - key[0] * self._chunk_tile_count, world_c + delta_c - key[1] * self._chunk_tile_count
                tile = chk.get_tile_at(inner_r, inner_c)
                assert tile
                tiles.append(tile)
        return tiles

    def spawn(self, x, y, config):
        """
        Spawn an entity at position (x,y) with config.
        :param x:
        :param y:
        :param config:
        :return:
        """
        key = self.xy2rc(x, y)
        chk = self._chunks.get(key)
        assert chk, 'pos (%s,%s) not in any chunk' % (x, y)
        obj = self._spawner.spawn(x, y, config)
        chk.add_object(obj)
        return obj

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
                    new_obj = self._spawner.spawn(x, y, obj_info)
                    assert new_obj
                    new_chunk.add_object(new_obj)
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
        #x = 0
        #y = 0
        all_keys = set()
        r, c = self.xy2rc(x, y)
        self._center_chunk_id = (r, c)
        # 更新并创建不存在的chunk
        for (r, c) in self._iter_chunk_keys(r, c):
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
        # 测试chunk数量始终可以保持在9个
        import random
        for i in range(32):
            r = int(random.random() * 1000)
            c = int(random.random() * 1000)
            cm.on_update(r, c, 0.5)
            self.assertEqual(len(set(cm.get_chunk_ids())), 9)

    def test_random_update_pos(self):
        # 测一下能不能随机update位置
        cm = ChunkManager(10, 1)
        import random
        for i in range(100):
            cm.on_update((random.random() - .5) * 100, (random.random() - .5) * 100, 0.5)

    def test_update_pos(self):
        cm = ChunkManager(10, 1)
        cm.set_generator(TilesOnlyMapGenerator())
        cm.on_update(4.5, 3.2, 0.5)

        tiles = cm.get_around_tiles(2.1, 3.1, 1)
        rc_list = [(t.r, t.c) for t in tiles]
        self.assertEqual(set(rc_list), set([
            (4, 1), (4, 2), (4, 3),
            (3, 1), (3, 2), (3, 3),
            (2, 1), (2, 2), (2, 3),
        ]))

        tiles = cm.get_around_tiles(9.1, 0.1, 1)
        rc_list = [(t.r, t.c) for t in tiles]
        self.assertEqual(set(rc_list), set([
            (1, 8), (1, 9), (1, 0),
            (0, 8), (0, 9), (0, 0),
            (9, 8), (9, 9), (9, 0),
        ]))

        self.assertEqual(len(cm.get_around_tiles(2, 3, 1)), 9)
        self.assertEqual(len(cm.get_around_tiles(2, 3, 3)), 49)
        self.assertEqual(len(cm.get_around_tiles(5.1, 5.1, 20)), 900)

    def test_spawn(self):
        cm = ChunkManager(10, 1)
        cm.set_generator(TilesOnlyMapGenerator())
        cm.on_update(4.5, 3.2, 0.5)
        box = cm.spawn(3.2, 13.4, {'name': 'box'})
        tiles = cm.get_around_tiles(3.2, 13.4, 0)
        self.assertEqual(len(tiles), 1)
        self.assertEqual(len(tiles[0].objects), 1)
        self.assertEqual(box, tiles[0].objects[0])

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



