# encoding: utf8

from base_component import BaseComponent
from variable.global_vars import G
import config as gconf


class ObjInspectable(BaseComponent):
    name = 'inspectable'

    def __init__(self, config):
        self._iname = config.get('iname', 'NAME_UNSET')

    def on_inspect(self):
        return "inspecting: %s" % self._iname


class ObjModel(BaseComponent):
    name = 'model'

    def __init__(self, config):
        model_path = config['model_file']
        loader = G.loader
        box = loader.loadModel(model_path)
        box.setName("box")
        box.reparentTo(G.render)
        self.node_path = box

        physics_config = config.get('physics')
        self.physical_np = None
        if physics_config:
            self.physical_np = G.physics_world.addBoxCollider(box, mass=30, bit_mask=gconf.BIT_MASK_OBJECT)
            self.physical_np.setTag("type", "box")
        assert self.physical_np, '%s %s' % (config, physics_config)

    def get_np(self):
        return self.node_path

    def get_physics_np(self):
        return self.physical_np
