# encoding: utf8


import chunk


class ChunkManager(object):
    def __init__(self):
        self._chunks = {}
        self._chunk_tile_count = 10  # chunk中的tile的数量
        self._chunk_tile_size = 1.  # tile在世界中的尺寸
        self._chunk_size = self._chunk_tile_count * self._chunk_tile_size  # chunk在世界中的尺寸
        self._center_chunkid = (0, 0)

    def __str__(self):
        strs = []
        for chunk_id, chunk_data in self._chunks.iteritems():
            strs.append(str(chunk_id))
        return '\t'.join(strs)

    def xy2rc(self, x, y):
        c = int(x / self._chunk_size)
        r = int(y / self._chunk_size)
        return r, c

    def rc2xy(self, r, c):
        return c * self._chunk_size, r * self._chunk_size

    def _iter_chunks(self, r, c):
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                yield r + dr, c + dc

    def _load_chunk(self, r, c):
        bx, by = self.rc2xy(r, c)
        return chunk.Chunk(self, bx, by, self._chunk_tile_count, self._chunk_tile_size)

    def _destroy_chunk(self, chunk_id):
        self._chunks[chunk_id] = None

    def on_update(self, x, y):
        keys = set()
        r, c = self.xy2rc(x, y)
        self._center_chunkid = (r, c)
        for (r, c) in self._iter_chunks(r, c):
            key = (r, c)
            keys.add(key)
            existing_chunk = self._chunks.get(key)
            if not existing_chunk:
                existing_chunk = self._load_chunk(r, c)
                self._chunks[key] = existing_chunk
        for chunk_id in self._chunks.keys():
            if chunk_id not in keys:
                self._destroy_chunk(chunk_id)

import unittest
import logging

class ChunkManagerTest(unittest.TestCase):
    def test_transform_xy_rc(self):
        pass


if __name__ == '__main__':
    unittest.main()



