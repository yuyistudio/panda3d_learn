# encoding: utf8

__author__ = 'Leon'


import json
from util import log
from entity_system.object_entity import ObjectEntity
from panda3d.core import Vec3
from variable.global_vars import G


class Spawner(object):
    def __init__(self):
        ObjectEntity.set_object_config(G.res_mgr.get_object_config())

    def spawn_default(self, name, x=0, y=0):
        ent = ObjectEntity(name)
        ent.set_pos(Vec3(x, y, 0))
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




