# encoding: utf8

__author__ = 'Leon'

"""
处理ground的geometry相关
"""

import time
from util import procedural_model, log
from panda3d.core import Vec3, Texture
from variable.global_vars import G
import copy


DEFAULT_UV = (0, 0, 1., 1.)


class GroundGeomUtil(object):
    def __init__(self, tile_size, tile_count, map_generator, texture_config):
        self._chunk_tile_size = tile_size
        self._chunk_tile_count = tile_count
        self._chunk_size = tile_size * tile_count
        self._generator = map_generator
        self._texture_config = texture_config
        self._side_uv = texture_config['tiles'][map_generator.get_side_name()]

    def _tile_info_to_uv_info(self, info):
        if not info:
            return None
        tile = info.get('tile')
        assert tile
        uv = self._texture_config['tiles'][tile['name']]
        side_name = tile.get('side_name')
        side_uv = uv
        if side_name:
            side_uv = self._texture_config['tiles'][side_name]
        level = tile.get('level', 0)
        ground_data = {'uv': uv, 'level': level, 'side_uv': side_uv}
        return ground_data

    def _storage_key(self, r, c):
        return '%d_%d' % (r, c)

    def new_ground_geom(self, r, c):
        storage_data = {}  # 存ground数据，放到chunk里面存折，后面载入的时候会用到.
        cache = {}
        for tile_r in range(-1, self._chunk_tile_count + 1):
            for tile_c in range(-1, self._chunk_tile_count + 1):
                info = self._generator.get(r * self._chunk_tile_count + tile_r, c * self._chunk_tile_count + tile_c)
                storage_data[self._storage_key(tile_r, tile_c)] = copy.deepcopy(info)
                cache[(tile_r, tile_c)] = self._tile_info_to_uv_info(info)
        plane_geom_node = procedural_model.create_plane(
            self._side_uv, self._chunk_tile_size, self._chunk_tile_count, cache)
        plane_np = G.render.attach_new_node(plane_geom_node)
        plane_np.set_pos(Vec3(c * self._chunk_size, r * self._chunk_size, 0))
        texture_file = None
        if self._texture_config:
            texture_file = self._texture_config['texture_file']
            tex = G.loader.loadTexture(texture_file)
            tex.set_magfilter(Texture.FT_linear_mipmap_linear)
            plane_np.set_texture(tex)
        return plane_np, {
            'tiles'  : storage_data,
            'texture': texture_file,
        }

    def create_ground_from_data(self, r, c, data):
        mapping = {}
        for key, info in data['tiles'].iteritems():
            key = key.split('_')
            mapping[(int(key[0]), int(key[1]))] = self._tile_info_to_uv_info(info)
        plane_geom_node = procedural_model.create_plane(
            self._side_uv, self._chunk_tile_size, self._chunk_tile_count, mapping)
        plane_np = G.render.attach_new_node(plane_geom_node)
        plane_np.set_pos(Vec3(c * self._chunk_size, r * self._chunk_size, 0))
        texture_file = data['texture']
        if texture_file:
            tex = G.loader.loadTexture(texture_file)
            tex.set_magfilter(Texture.FT_nearest)
            tex.setWrapU(Texture.WM_repeat)
            tex.setWrapV(Texture.WM_repeat)
            plane_np.set_texture(tex)
        return plane_np
