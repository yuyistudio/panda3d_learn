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
from util import procedural_model
from variable.global_vars import G
from panda3d.core import Texture
#from panda3d.core import Thread
#assert Thread.isThreadingSupported()
#from direct.stdpy import thread
import time


DEFAULT_UV = (0, 0, 1., 1.)


class LRUCache(object):
    def __init__(self, max_count=6):
        self._keys = []
        self._hash = {}
        self._max_keys = max_count

    def debug_peek(self, key):
        return self._hash.get(key)

    def add(self, key, value):
        """
        Add one, and probably returns one obsolete value.
        :param key:
        :param value:
        :return:
        """
        assert key not in self._hash
        trash_key = None
        trash_value = None
        if len(self._keys) == self._max_keys:
            trash_key = self._keys[0]
            trash_value = self._hash[trash_key]
            self._keys.pop(0)
            del self._hash[trash_key]
        self._keys.append(key)
        self._hash[key] = value
        return trash_key, trash_value

    def get(self, key):
        """
        Get and remove.
        :param key:
        :return:
        """
        try:
            idx = self._keys.index(key)
        except:
            return None
        self._keys.pop(idx)
        v = self._hash[key]
        del self._hash[key]
        return v


class ChunkManager(object):
    def __init__(self, chunk_title_count=10, chunk_tile_size=1.):
        """
        :param chunk_title_count: chunk中的tile的数量
        :param chunk_tile_size: tile在世界中的尺寸
        :return:
        """
        self._storage_mgr = None
        self._texture_config = None
        self._chunk_tile_count = chunk_title_count
        self._chunk_tile_size = chunk_tile_size
        self._chunks = {}
        self._chunk_size = self._chunk_tile_count * self._chunk_tile_size  # chunk在世界中的尺寸
        self._center_chunk_id = (0, 0)
        self._generator = DefaultRandomMapGenerator()
        self._spawner = DefaultEntitySpawner()
        self._cache = LRUCache(1)  # TODO 根据机器内存大小动态设置一个合理的值。

        self._yielders = []
        self._loading_chunk_keys = []

    def set_storage_mgr(self, storage_mgr):
        """
        :param storage_mgr:
            set(k, v)
            get(k, v)
        :return:
        """
        self._storage_mgr = storage_mgr

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
        assert generator
        self._generator = generator

    def set_tile_texture(self, texture_config):
        """
        :param texture_config:
            {
                "texture_file": "xxx",
                "tiles": {
                    "tile_name": (u1,v1,u2,v2),
                }
            }
        :return:
        """
        self._texture_config = texture_config

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

    def _iter_chunk_keys(self, x, y, topn=12):
        """
        按照某种规则，返回点(x,y)附近需要载入的方块。
        :param x:
        :param y:
        :param topn: 返回距离主角最近的topn个chunk, 至少4个。
        :return:
        """
        assert topn >= 4
        center_r, center_c = self.xy2rc(x, y)
        max_size = 3  # 搜索半径
        result = []
        for dr in range(-max_size, max_size+1):
            for dc in range(-max_size, max_size+1):
                r, c = center_r + dr, center_c + dc
                tx, ty = self.rc2xy(r, c)

                tx += self._chunk_size * .5
                ty += self._chunk_size * .5
                dist_sq = (tx - x) ** 2 + (ty - y) ** 2
                result.append((dist_sq, (r, c)))
        # 排序并返回
        result.sort(key=lambda v: v[0])
        for v in result[:topn]:
            yield v[1]

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

    def spawn_to_exist_chunk(self, x, y, config):
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
        assert sys.getrefcount(obj) == 2
        chk.add_object(obj)
        return obj

    def _create_ground_from_data(self, r, c, data):
        mapping = {}
        for item in data['tiles']:
            mapping[(item[0], item[1])] = item[2]

        def uv_fn(tile_r, tile_c):
            name = mapping.get((tile_r, tile_c))
            if not name:
                assert name, 'no data found for tile (%s,%s)' % (tile_r, tile_c)
                return DEFAULT_UV
            uv = self._texture_config['tiles'].get(name)
            assert uv, 'texture config not found: %s, from %s' % (name, self._texture_config)
            return uv
        plane_geom_node = procedural_model.create_plane(self._chunk_tile_size, self._chunk_tile_count, uv_fn)
        plane_np = G.render.attach_new_node(plane_geom_node)
        plane_np.set_pos(Vec3(c * self._chunk_size, r * self._chunk_size, 0))
        texture_file = data['texture']
        if texture_file:
            tex = G.loader.loadTexture(texture_file)
            tex.set_magfilter(Texture.FT_nearest)
            plane_np.set_texture(tex)
        return plane_np

    def _new_ground_geom(self, r, c):
        tiles_data = []

        def uv_fn(tile_r, tile_c):
            info = self._generator.get(r * self._chunk_tile_count + tile_r, c * self._chunk_tile_count + tile_c)
            assert info
            name = info.get('tile', {}).get('name')
            tiles_data.append((tile_r, tile_c, name))  # 记录tile数据，以便日后使用
            if not name:
                assert name, 'tile has no name: %s' % info
                return DEFAULT_UV
            uv = self._texture_config['tiles'].get(name)
            assert uv, 'texture config not found: %s, from %s' % (name, self._texture_config)
            return uv

        plane_geom_node = procedural_model.create_plane(self._chunk_tile_size, self._chunk_tile_count, uv_fn)
        plane_np = G.render.attach_new_node(plane_geom_node)
        plane_np.set_pos(Vec3(c * self._chunk_size, r * self._chunk_size, 0))
        texture_file = None
        if self._texture_config:
            texture_file = self._texture_config['texture_file']
            tex = G.loader.loadTexture(texture_file)
            tex.set_magfilter(Texture.FT_nearest)
            plane_np.set_texture(tex)
        return plane_np, {
            'tiles': tiles_data,
            'texture': texture_file,
        }

    def _load_chunk(self, r, c):
        # 从缓存中载入
        cache_value = self._cache.get((r, c))
        if cache_value:
            self._chunks[(r, c)] = cache_value
            t1 = time.time()
            cache_value.set_enabled(True)
            print 'load from cache:', time.time() - t1
            return cache_value

        t1 = time.time()
        # 重新载入
        bx, by = self.rc2xy(r, c)
        new_chunk = chunk.Chunk(self, bx, by, self._chunk_tile_count, self._chunk_tile_size)
        if self._storage_mgr:
            storage_data = self._storage_mgr.get(str((r, c)))
            if storage_data:
                new_chunk.on_load(self._spawner, storage_data)
                ground_data = new_chunk.get_ground_data()
                assert ground_data
                ground_np = self._create_ground_from_data(r, c, ground_data)
                new_chunk.set_ground_geom(ground_np, ground_data)
                return new_chunk

        # 生成tile物体
        plane_np, tiles_data = self._new_ground_geom(r, c)
        new_chunk.set_ground_geom(plane_np, tiles_data)

        # 遍历所有tile生成物体
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
                    assert new_obj  # 确保spawner可以返回正确的值
                    assert sys.getrefcount(new_obj) == 2  # 确保不会spawner自己不会占用引用
                    new_chunk.add_object(new_obj)
                    assert sys.getrefcount(new_obj) == 3  # 确保被正确添加到了chunk中

        print 'load from scatch:', time.time() - t1
        return new_chunk

    def _unload_chunk(self, chunk_id):
        # 这里有个小坑，不能用 dict[key] = None 这种方式来删除key（在Lua中是可以的）。
        target_chunk = self._chunks[chunk_id]
        target_chunk.set_enabled(False)
        cache_key, cache_value = self._cache.add(chunk_id, target_chunk)
        del self._chunks[chunk_id]
        del chunk_id  # 防止误用

        # 删除过期的cache
        if cache_key:
            data = cache_value.on_unload()
            if self._storage_mgr:
                self._storage_mgr.set(str(cache_key), data)

    def on_update(self, x, y, dt):
        """
        根据位置进行更新，始终保持只有主角附近的chunk在内存中。
        :param x: 世界坐标x
        :param y: 世界坐标y
        :param dt: 单位秒
        :return: None
        """
        #x, y = 0, 0
        all_keys = set()
        # 更新并创建不存在的chunk
        for (r, c) in self._iter_chunk_keys(x, y):
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
        # 执行yielders
        remained_yielders = []
        for yielder in self._yielders:
            try:
                yielder.next()
                remained_yielders.append(yielder)
            except:
                pass
        self._yielders = remained_yielders

import unittest


class ChunkManagerTest(unittest.TestCase):
    def test_lru(self):
        lru = LRUCache(2)
        lru.add("k1", "v1")
        self.assertEqual(lru.debug_peek('k1'), 'v1')
        self.assertEqual(lru.debug_peek('k2'), None)
        lru.add("k2", "v2")
        self.assertEqual(lru.debug_peek('k2'), 'v2')
        lru.add("k3", "v3")
        self.assertEqual(lru.debug_peek('k1'), None)
        self.assertEqual(lru.debug_peek('k2'), 'v2')
        self.assertEqual(lru.get("k2"), "v2")
        lru.add("k4", "v4")
        self.assertEqual(lru.debug_peek('k3'), 'v3')
        lru.add("k5", "v5")
        self.assertEqual(lru.debug_peek('k3'), None)
        self.assertEqual(lru.get('k10086'), None)

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
        box = cm.spawn_to_exist_chunk(3.2, 13.4, {'name': 'box'})
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



