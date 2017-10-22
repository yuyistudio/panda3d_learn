# encoding: utf8

__author__ = 'Leon'


import json
from entity_system.object_entity import ObjectEntity
from panda3d.core import Vec3


class Spawner(object):
    def __init__(self):
        objects_definitions = 'assets/objects/objects.json'
        js = json.loads(open(objects_definitions, 'r').read())
        ObjectEntity.set_config(js)

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
        ent = ObjectEntity(storage_data)
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
        ent = ObjectEntity(storage_data)
        return ent



