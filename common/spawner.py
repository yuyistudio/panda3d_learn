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

    def spawn(self, x, y, config):
        ent = ObjectEntity(config)
        ent.set_pos(Vec3(x, y, 1))
        return ent
