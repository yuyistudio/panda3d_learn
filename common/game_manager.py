# encoding: utf8

__author__ = 'Leon'

from variable.global_vars import G
from util import log, random_util
from hero import create
from entity_system.base_components import ObjGroundItem
from chunk import chunk_manager, test_map_generator
from craft_system import craft_manager
from objects import ground, lights, box
from panda3d.core import Vec3
from inventory_system.inventory_manager import InventoryManager
import json
from util import fog
import random
from hero.tool import HeroEquipmentModels


class GameManager(object):
    chunk_tile_size = 2

    def __init__(self):
        self.scene = None
        self.map_generator = None
        self.hero = None
        self.equipment_models = None


        # 雾效
        f = .7
        self.fog = fog.LinearFog(f, f, f, 70, 140)
        G.accept('f', self.fog.switch)

        # 背包系统
        self.inventory = InventoryManager()
        def add_apples():
            self.give_hero_item_by_name('axe', 2)
            self.give_hero_item_by_name('sword', 2)

        G.accept('c', add_apples)

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

        # 载入inventory
        self.inventory.on_load(self.slot)

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

    def change_equipment_model(self, slot_name, equipment_name):
        self.equipment_models.change_model(slot_name, equipment_name)

    def quick_equip(self, bag, idx):
        """
        调用者确保bag[index]是一个可以装备的物品。
        :param bag:
        :param idx:
        :return:
        """
        return self.inventory.quick_equip(bag, idx)

    def get_mouse_item(self):
        return self.inventory.get_mouse_item()

    def give_hero_item(self, item):
        res = self.inventory.add_item(item)
        self.inventory.refresh_inventory()
        return res

    def give_hero_item_by_name(self, name, count):
        """
        用于玩家获取新物品。如果放不下了，则放到地上。
        :param name:
        :param count:
        :return:
        """
        # 获取每样物品的最大堆叠
        max_stack_count = 1
        com_config = G.res_mgr.get_item_config_by_name(name)['components']
        stackable = com_config.get('stackable')
        if stackable:
            max_stack_count = stackable.get('max_count', 1)

        # 添加到背包
        while count > 0:
            remained_item = self.inventory.create_to_inventory(name, min(count, max_stack_count))
            count -= max_stack_count
            if remained_item:
                # 添加失败时，将剩余的物品全部放到地面上
                center_pos = self.hero.get_pos()
                radius = self.hero.get_radius() * 2
                self.put_item_on_ground(remained_item, center_pos, radius)
                self.create_item_on_ground(center_pos, radius, name, count)
                break
        self.inventory.refresh_inventory()

    def put_mouse_item_on_ground(self, pos):
        mouse_item = self.inventory.take_mouse_item()
        self.inventory.get_mouse_item()
        ground_item = G.spawner.spawn_ground_item(mouse_item, pos, 0)
        ground_item.get_component(ObjGroundItem).set_freeze_time(3)
        self.chunk_mgr.add_ground_item(ground_item)
        self.inventory.refresh_mouse()

    def put_item_on_ground(self, item, center_pos, radius):
        ground_item = G.spawner.spawn_ground_item(item, center_pos, radius)
        self.chunk_mgr.add_ground_item(ground_item)

    def create_item_on_ground(self, center_pos, radius, name, count):
        max_stack_count = self._get_max_stack_count(name)
        while count > 0:
            item = self.inventory.create_item(name, min(count, max_stack_count))
            count -= max_stack_count
            ground_item = G.spawner.spawn_ground_item(item, center_pos, radius)
            self.chunk_mgr.add_ground_item(ground_item)

    def _get_max_stack_count(self, name):
        # 获取每样物品的最大堆叠
        max_stack_count = 1
        com_config = G.res_mgr.get_item_config_by_name(name)['components']
        stackable = com_config.get('stackable')
        if stackable:
            max_stack_count = stackable.get('max_count', 1)
        return max_stack_count

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

        self.equipment_models = HeroEquipmentModels(self.hero)

    def save_scene(self):
        self.inventory.on_save(self.slot)
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





