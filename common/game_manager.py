# encoding: utf8

__author__ = 'Leon'

from variable.global_vars import G
from util import log
from hero import create
from chunk import chunk_manager, test_map_generator
from craft_system import craft_manager
from objects import ground, lights, box
from panda3d.core import Vec3
import json


class GameManager(object):
    def __init__(self):
        # TODO remove it
        self.hero = G.spawner.spawn_default('hero', 3, 3)
        G.operation.set_target(self.hero)

        log.process('creating craft manager')
        self.craft_mgr = craft_manager.CraftManager()
        self.craft_mgr.register_recipes(json.loads(open('assets/json/recipes.json').read()))

        log.process('creating chunk manager')
        self.chunk_mgr = chunk_manager.ChunkManager(chunk_title_count=8, chunk_tile_size=2, chunk_count=36)
        self.chunk_mgr.set_generator(G.config_mgr.get_map_config('perlin')())
        self.chunk_mgr.set_tile_texture(G.config_mgr.get_tile_config('default'))
        self.chunk_mgr.set_spawner(G.spawner)

        # 载入存档
        log.process('loading slot storage')
        self.slot = G.storage_mgr.get_or_create_slot_entry( G.context.slot_name )
        G.storage_mgr.save_slots_entry()
        if self.slot.load():
            log.process('slot storage loaded')
        else:
            log.process('slot storage not found')
        self.scene = self.slot.get_current_scene()
        if self.scene:
            log.process('storage scene found: %s', self.scene)
            self.scene.load()
        else:
            log.process('creating new scene')
            self.scene = self.slot.create_scene( G.context.default_scene )
            log.process('saving new scene')
            self.slot.save()

        # 设置chunk manager的存档
        self.chunk_mgr.set_storage_mgr(self.scene)

        self._ground = ground.create()  # TODO remove it
        self._lights = lights.create()  # TODO remove it

    def save_scene(self):
        self.chunk_mgr.on_save()
        self.scene.save()
        self.slot.save()

    def on_update(self, dt):
        # TODO remove it
        self.hero.on_update(dt)

        pos = G.operation.get_center_pos()
        self.chunk_mgr.on_update(pos[0], pos[1], dt)





