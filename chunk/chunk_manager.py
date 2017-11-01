# encoding: utf8


"""
几个rc的概念：
    chunk_rc  chunk的世界坐标坐标
    world_rc  tile的世界坐标
    tile_rc   tile在chunk内的本地坐标
ChunkManager的rc函数使用chunk_rc.
Chunk的rc函数使用tile_rc.
"""

import traceback
import chunk
from map_generator import *
import math
from util import procedural_model, log
from variable.global_vars import G
from panda3d.core import Texture
#from panda3d.core import Thread
#assert Thread.isThreadingSupported()
import time
from util import async_loader
from lru_cache import LRUCache
from ground_geom import GroundGeomUtil


class ChunkManager(object):
    def __init__(self,
                 texture_config, spawner, map_generator, storage_mgr,
                 chunk_title_count=16, chunk_tile_size=2., chunk_count=9,
                 ):
        """
        :param chunk_title_count: chunk中的tile的数量
        :param chunk_tile_size: tile在世界中的尺寸
        :return:
        """
        self._tile_not_found_exception = Exception('tile not found')

        self._chunk_count = chunk_count
        self._storage_mgr = storage_mgr
        self._chunk_tile_count = chunk_title_count
        self._chunk_tile_size = chunk_tile_size
        self._chunks = {}
        self._chunk_size = self._chunk_tile_count * self._chunk_tile_size  # chunk在世界中的尺寸
        self._center_chunk_id = (0, 0)
        self._generator = map_generator
        self._spawner = spawner
        self._cache = LRUCache(11)  # TODO 根据机器内存大小动态设置一个合理的值。
        self._async_loader = async_loader.AsyncLoader()
        self._async_loader.start()
        self._yielders = []
        self._processing_chunk_keys = []  # 当前正在加载的ChunkIDs（加载分为很多帧进行的）
        self._ground_geom_util = GroundGeomUtil(self._chunk_tile_size, self._chunk_tile_count, map_generator, texture_config)

        from collections import Counter
        self._unload_counter = Counter()
        self._counter_threshold = 0 if G.debug else 200

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
        """
        尝试将物体从src_chunk移动到正确的chunk中.
        :param src_chunk:
        :param frozen_object:
        :return:
        """
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

    def _iter_chunk_keys(self, x, y):
        """
        按照某种规则，返回点(x,y)附近需要载入的方块。
        :param x:
        :param y:
        :return:
        """
        center_r, center_c = self.xy2rc(x, y)
        result = []
        for dr in range(-1, 18):
            for dc in range(-3, 4):
                r, c = center_r + dr, center_c + dc
                tx, ty = self.rc2xy(r, c)

                tx += self._chunk_size * .5
                ty += self._chunk_size * .5
                dist_sq = (tx - x) ** 2 + (ty - y) ** 2
                result.append((dist_sq, (r, c)))
        # 排序并返回
        result.sort(key=lambda v: v[0])
        for v in result[:self._chunk_count]:
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

    def on_save(self):
        """
        保存当前所有信息到storage_mgr
        :return:
        """
        for key, value in self._chunks.iteritems():
            self._storage_mgr.set(str(key), value.on_save())

    def destroy(self):
        """
        离开当前地图时调用，销毁所有chunk。
        Warning：赢得先调用on_save保存当前地图。
        :return:
        """
        for chk in self._chunks.itervalues():
            chk.destroy()
        # TODO 考虑正在载入的部分

    def on_load(self):
        """
        不需要on_load函数，载入on_update时动态载入。
        :return:
        """
        assert False

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

    def _load_chunk(self, r, c):
        chunk_self = self
        chunk_key = (r, c)
        assert chunk_key not in self._processing_chunk_keys
        self._processing_chunk_keys.append(chunk_key)

        def wrapper():
            chunk = None
            try:
                assert not self._chunks.get(chunk_key)
                chunk = self._load_chunk_real(r, c)
                assert not self._chunks.get(chunk_key), '防止chunk._load_chunk_real()中不小心赋值'
                if chunk:
                    fn = chunk.get_flatten_fn()
                    if fn:
                        fn()
            finally:
                # 确保 _processing_chunk_keys 里面的值始终正确
                chunk_self._processing_chunk_keys.remove(chunk_key)
                if chunk:
                    self._chunks[chunk_key] = chunk
        self._async_loader.add_job(wrapper)

    def _load_chunk_real(self, r, c):
        """
        :param r:
        :param c:
        :return:
        """
        chunk_key = (r, c)
        bx, by = self.rc2xy(r, c)

        # 从缓存中载入
        cache_value = self._cache.get(chunk_key)
        if cache_value:
            cache_value.set_enabled(True)
            return cache_value

        # 从存档种载入
        new_chunk = chunk.Chunk(self, bx, by, self._chunk_tile_count, self._chunk_tile_size)
        if self._storage_mgr:
            storage_data = self._storage_mgr.get(str((r, c)))
            if storage_data:
                new_chunk.on_load(self._spawner, storage_data)
                ground_data = new_chunk.get_ground_data()
                assert ground_data
                ground_np = self._ground_geom_util.create_ground_from_data(r, c, ground_data)
                new_chunk.set_ground_geom(ground_np, ground_data)
                return new_chunk

        # 生成tile物体和地形
        plane_np, tiles_data = self._ground_geom_util.new_ground_geom(r, c)
        new_chunk.set_ground_geom(plane_np, tiles_data)

        # 遍历所有tile生成物体
        # TODO 优化点，map_generator的get可以只调用一次吗？
        br = r * self._chunk_tile_count
        bc = c * self._chunk_tile_count
        for ir in range(br, br + self._chunk_tile_count):
            for ic in range(bc, bc + self._chunk_tile_count):
                ginfo = self._generator.get(ir, ic)
                if not ginfo:
                    continue
                obj_info = ginfo.get('object')
                if obj_info:
                    x = (ic + .5) * self._chunk_tile_size
                    y = (ir + .5) * self._chunk_tile_size
                    new_obj = self._spawner.spawn(x, y, obj_info)
                    assert new_obj  # 确保spawner可以返回正确的值
                    ref_count = sys.getrefcount(new_obj)
                    assert ref_count == 2, ref_count  # 确保spawner自己不会占用引用. new_obj占一个引用，参数占一个引用
                    new_chunk.add_object(new_obj)
                    assert sys.getrefcount(new_obj) == 3  # 确保被正确添加到了chunk中

        return new_chunk

    def _unload_chunk(self, chunk_key):
        self._unload_counter[chunk_key] += 1
        if self._unload_counter[chunk_key] < self._counter_threshold or random.random() < .5:
            return
        del self._unload_counter[chunk_key]

        chunk_self = self
        if chunk_key in self._processing_chunk_keys:
            return
        self._processing_chunk_keys.append(chunk_key)

        def wrapper():
            try:
                self._unload_chunk_real(chunk_key)
            finally:
                chunk_self._processing_chunk_keys.remove(chunk_key)
        self._async_loader.add_job(wrapper)

    def _unload_chunk_real(self, chunk_id):
        # 这里有个小坑，不能用 dict[key] = None 这种方式来删除key（在Lua中是可以的）。
        target_chunk = self._chunks[chunk_id]
        target_chunk.set_enabled(False)
        cache_key, cache_value = self._cache.add(chunk_id, target_chunk)
        del self._chunks[chunk_id]
        del chunk_id  # 防止误用

        # 删除过期的cache
        if cache_key:
            data = cache_value.on_save()
            cache_value.destroy()
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

        # 更新并创建不存在的chunk
        all_keys = set()
        for (r, c) in self._iter_chunk_keys(x, y):
            key = (r, c)
            del self._unload_counter[key]
            all_keys.add(key)
            existing_chunk = self._chunks.get(key)
            if not existing_chunk:
                if (r, c) not in self._processing_chunk_keys:
                    self._load_chunk(r, c)
                continue
            existing_chunk.on_update(dt)

        # 删除不在附近的chunk
        for chunk_id in self._chunks.keys():
            if chunk_id not in all_keys:
                self._unload_chunk(chunk_id)

        # 执行yielders. 纯粹是性能优化，可暂时忽略。
        remained_yielders = []
        for yielder in self._yielders:
            try:
                yielder.next()
                remained_yielders.append(yielder)
            except StopIteration:
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


if __name__ == '__main__':
    unittest.main()



