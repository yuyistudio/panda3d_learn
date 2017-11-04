# encoding: utf8

__author__ = 'Leon'



from entity_system.base_components import ObjGroundItem
from util import random_util
from entity_system.object_entity import ObjectEntity
from panda3d.core import Vec3
from variable.global_vars import G


class Spawner(object):
    def __init__(self):
        ObjectEntity.set_object_config(G.res_mgr.get_object_config())

    def spawn_ground_item(self, item, center_pos, radius):
        x, y = random_util.pos_around(center_pos, radius)
        ground_item_object = G.spawner.spawn_default('ground_item', x, y, 1)
        ground_item_com = ground_item_object.get_component(ObjGroundItem)
        assert ground_item_com
        ground_item_com.set_item(item)
        return ground_item_object

    def spawn_default(self, name, x=0, y=0, z=0):
        ent = ObjectEntity(name)
        ent.set_pos(Vec3(x, y, z))
        return ent

    def spawn(self, x, y, config):
        """
        :param x:
        :param y:
        :param config:
            {
                "name": "box",
                "components": {
                }
            }
        :return:
        """
        assert isinstance(config, object), config
        ent = ObjectEntity(config['name'], config)
        ent.set_pos(Vec3(x, y, 0))
        return ent

    def spawn_from_storage(self, storage_data):
        """
        :param storage_data:
            {
                "name": "box",
                "components": {
                }
            }
        :return:
        """
        ent = ObjectEntity(storage_data['name'], storage_data)
        return ent




