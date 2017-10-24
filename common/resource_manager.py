# encoding: utf8


"""
管理texture static_model
"""

from variable.global_vars import G


class ResourceManager(object):
    def __init__(self):
        self._models = {}
        self._textures = {}

    def get_static_model(self, filepath):
        model = self._models.get(filepath)
        if not model:
            model = G.loader.loadModel(filepath)
        return model

    def get_texture(self, filepath):
        texture = self._textures.get(filepath)
        if not texture:
            texture = G.loader.loadTexture(filepath)
        return texture
