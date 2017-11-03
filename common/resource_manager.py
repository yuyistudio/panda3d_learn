# encoding: utf8


"""
管理texture static_model
"""

from variable.global_vars import G
from util import storage
from panda3d.core import Texture

ITEM_PATH_FORMAT = "assets/images/items/%s"


class ResourceManager(object):
    def __init__(self):
        self._models = {}
        self._textures = {}
        self._scenes = storage.load_json_file('assets/json/scenes.json')
        self._item_config = storage.load_json_file('assets/json/items.json')
        self._object_config = storage.load_json_file('assets/json/objects.json')
        assert self._scenes and self._item_config and self._object_config

        self._item_textures = {}
        images = 'apple axe orange iron silver sapling cooking_pit cobweb'.split()
        for image_path in images:
            full_path = ITEM_PATH_FORMAT % (image_path + '.png')
            used_texture = G.loader.loadTexture(full_path)
            used_texture.set_magfilter(Texture.FT_nearest)
            self._item_textures[full_path] = used_texture

    def get_static_model(self, filepath):
        model = self._models.get(filepath)
        if not model:
            model = G.loader.loadModel(filepath)
        return model

    def get_texture(self, filepath):
        texture = self._textures.get(filepath)
        if not texture:
            texture = G.loader.loadTexture(filepath)
            self._textures[filepath] = texture
        return texture

    def get_scene_config(self, scene_name):
        return self._scenes.get(scene_name)

    def get_object_config(self):
        return self._object_config

    def get_item_config(self):
        return self._item_config

    def get_item_config_by_name(self, item_name):
        return self._item_config.get(item_name)

    def get_item_texture(self, image_path):
        return self._item_textures.get(image_path)

