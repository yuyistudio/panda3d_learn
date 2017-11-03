# encoding: utf8

__author__ = 'Leon'


import json
from entity_system.base_entity import BaseEntity
from panda3d.core import Vec3


class Spawner(object):
    def __init__(self):
        objects_definitions = 'assets/json/objects.json'
        js = json.loads(open(objects_definitions, 'r').read())
        BaseEntity.set_config(js)

    def spawn_default(self, name, x=0, y=0):
        ent = BaseEntity(name)
        ent.set_pos(Vec3(x, y, 0))
        return ent

    def spawn(self, x, y, storage_data):
        """
        :param x:
        :param y:
        :param storage_data:
            {
                "name": "box",
                "components": {
                }
            }
        :return:
        """
        assert isinstance(storage_data, object), storage_data
        ent = BaseEntity(storage_data['name'], storage_data)
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
        ent = BaseEntity(storage_data['name'], storage_data)
        return ent



