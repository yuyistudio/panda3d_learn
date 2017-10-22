# encoding: utf8

__author__ = 'Leon'

import json


class ConfigManager(object):
    def __init__(self):
        self.tile_configs = {}
        self.map_configs = {}

    @staticmethod
    def _load_tile_config(filename):
        js = json.loads(open(filename).read())
        tile_names = js.get('tile_names')
        if tile_names:
            rows = len(tile_names)
            cols = len(tile_names[0])
            res = {}
            for row in range(rows):
                for col in range(cols):
                    tile_name = tile_names[row][col]
                    if not tile_name:
                        continue
                    u, v = 1. * col / cols, 1. * (rows - row - 1) / rows
                    u2, v2 = u + 1. / cols, v + 1. / rows
                    res[tile_name] = (u, v, u2, v2)
        else:
            assert False
        return res

    def register_tile_config(self, name, config):
        """
        :param name: config name.
        :param config: string for file path,
            or json:
            {
                "texture_file": "xxx",
                "tiles": {
                    "tile_name": (u1,v1,u2,v2),
                }
            }
        :return:
        """
        assert name not in self.tile_configs
        if isinstance(config, str):
            self.tile_configs[name] = {
                'tiles': ConfigManager._load_tile_config(config),
                'texture_file': config.replace('.json', '.png')
            }
        elif isinstance(config, object):
            self.tile_configs[name] = config
        else:
            assert 'invalid tile config: %s' % config

    def get_tile_config(self, name):
        return self.tile_configs.get(name)

    def register_map_config(self, name, config):
        assert name not in self.map_configs
        self.map_configs[name] = config

    def get_map_config(self, name):
        return self.map_configs.get(name)



