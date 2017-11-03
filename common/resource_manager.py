# encoding: utf8


"""
管理texture static_model
"""

from variable.global_vars import G
from util import storage


class ResourceManager(object):
    def __init__(self):
        self._models = {}
        self._textures = {}
        self._scenes = storage.load_json_file('assets/json/scenes.json')
        assert self._scenes

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

