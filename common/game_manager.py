# encoding: utf8

__author__ = 'Leon'

from variable.global_vars import G
from util import log
from hero import create
from chunk import chunk_manager, test_map_generator
from craft_system import craft_manager
from objects import ground, lights, box
from panda3d.core import Vec3
from inventory_system.inventory import Inventory
import json
from util import fog


class GameManager(object):
    chunk_tile_size = 2

    def __init__(self):
        self.scene = None
        self.map_generator = None
        self.hero = None

        # 雾效
        f = .7
        self.fog = fog.LinearFog(f, f, f, 70, 140)
        G.accept('f', self.fog.switch)

        # 背包系统
        self.inventory = Inventory()

        # 制造系统
        log.process('creating craft manager')
        self.craft_mgr = craft_manager.CraftManager()
        self.craft_mgr.register_recipes(json.loads(open('assets/json/recipes.json').read()))

        # 载入存档
        log.process('loading slot storage')
        self.slot = G.storage_mgr.get_or_create_slot_entry(G.context.slot_name)
        G.storage_mgr.save_slots_entry()
        if self.slot.load():
            log.process('slot storage loaded')
            self.switch_to_scene(None)
        else:
            log.process('slot storage not found, entering default scene')
            self.switch_to_scene('default')

        # 设置chunk manager的存档
        log.process('creating chunk manager')
        self.chunk_mgr = chunk_manager.ChunkManager(
            texture_config=G.config_mgr.get_tile_config('default'),
            spawner=G.spawner,
            map_generator= self.map_generator,
            storage_mgr=self.scene,
            chunk_title_count=10, chunk_tile_size=self.chunk_tile_size, chunk_count=36)

        self._ground = ground.create()  # TODO remove it
        lights.create()  # TODO remove it

    def switch_to_scene(self, scene_name):
        """
        进入到场景。
        :param scene_name: 场景名称，必须全局唯一
        :return:
        """
        scene_config = G.res_mgr.get_scene_config(scene_name)

        # 保存当前scene的数据
        if self.scene and self.hero:
            pos = self.hero.get_pos()
            self.scene.set('hero_pos', (pos[0], pos[1]))

        # 切换scene
        if not scene_name:
            scene_name = self.slot.get_current_scene()
            assert scene_name
        self.scene = self.slot.switch_to_scene(scene_name)
        if not self.scene:
            log.error('%s', self.slot.get_current_scene())
        assert self.scene
        self.slot.save()
        is_new_scene = not self.scene.load()

        # 地图生成器
        self.map_generator = G.config_mgr.get_map_config(scene_config['map_generator'])()

        # 载入英雄数据
        if self.hero:
            if is_new_scene:
                log.process('set hero to new position')
                r, c = self.map_generator.get_start_tile()
                self.hero.set_pos(c * self.chunk_tile_size, r * self.chunk_tile_size)
            else:
                log.process('set hero to old position')
                x, y = self.scene.get('hero_pos')
                self.hero.set_pos(x, y, 0)
        else:
            if is_new_scene:
                log.process("creating new hero")
                pos = self.map_generator.get_start_tile()
                self.hero = G.spawner.spawn_default('hero', pos[1] * self.chunk_tile_size,
                                                    pos[1] * self.chunk_tile_size)
            else:
                log.process('creating hero from storage data')
                hero_data = self.slot.get('hero')
                self.hero = G.spawner.spawn_from_storage(hero_data)
            assert self.hero
            G.operation.set_target(self.hero)

    def save_scene(self):
        self.chunk_mgr.on_save()
        self.slot.set('hero', self.hero.on_save())
        self.scene.save()
        self.slot.save()

    def on_update(self, dt):
        # TODO remove it
        self.hero.on_update(dt)
        pos = G.operation.get_center_pos()
        G.dir_light.set_pos(pos)
        self.chunk_mgr.on_update(pos[0], pos[1], dt)





