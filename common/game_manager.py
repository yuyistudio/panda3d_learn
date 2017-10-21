# encoding: utf8

__author__ = 'Leon'

from variable.global_vars import G
from operation import operation
from hero import create
from chunk import chunk_manager, test_map_generator
from craft_system import craft_manager
from objects import ground, lights, box
from panda3d.core import Vec3
import json


class GameManager(object):
    def __init__(self):
        self.hero = create.Hero()
        self.operation = operation.Operation(self.hero)
        self.craft_mgr = craft_manager.CraftManager()
        self.craft_mgr.register_recipes(json.loads(open('assets/json/recipes.json').read()))
        self.chunk_mgr = chunk_manager.ChunkManager(3, 3)
        self.chunk_mgr.set_generator(test_map_generator.TestMapGenerator())
        self.chunk_mgr.set_spawner(G.spawner)

        self._ground = ground.create()  # TODO remove it
        self._lights = lights.create()  # TODO remove it

    def on_update(self, dt):
        self.hero.onUpdate(dt)
        pos = self.hero.getNP().getPos()
        self.chunk_mgr.on_update(pos.getX(), pos.getY(), dt)





