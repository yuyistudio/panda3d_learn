# encoding: utf8

from base_component import BaseComponent
from variable.global_vars import G
import config as gconf
from panda3d.core import Vec3, Texture


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
        self.scale = config.get('scale', 1.)
        self.collider_scale = config.get('collider_scale', 1.)
        self.is_static = config.get('static', True)  # TODO 对于静态物体，可以合并模型进行优化. np.flatten_strong()
        loader = G.loader
        box = loader.loadModel(model_path)
        box.setName("box")
        box.reparentTo(G.render)
        self.model_np = box
        self.model_np.set_scale(self.scale)
        self.model_np.set_pos(Vec3(0, 0, 0))
        for tex in self.model_np.find_all_textures():
            tex.set_magfilter(Texture.FT_nearest)
            tex.set_minfilter(Texture.FT_linear)

        physics_config = config.get('physics')
        self.physical_np = None
        if physics_config:
            self.physical_np = G.physics_world.addBoxCollider(
                box, mass=0, bit_mask=gconf.BIT_MASK_OBJECT,
                reparent=not self.is_static,
                scale=self.collider_scale,
            )
            self.physical_np.setTag("type", "box")
            body = self.physical_np.node()
            body.setDeactivationEnabled(True)
            body.setDeactivationTime(1.0)
        assert self.physical_np, '%s %s' % (config, physics_config)

    def set_enabled(self, enabled):
        G.physics_world.set_collider_enabled(self.physical_np, enabled)
        if enabled:
            if self.is_static:
                self.model_np.reparent_to(G.render)
            else:
                self.physical_np.reparent_to(G.render)
        else:
            if self.is_static:
                self.model_np.detach_node()
            else:
                self.physical_np.detach_node()

    def destroy(self):
        G.physics_world.remove_collider(self.physical_np)
        self.physical_np.remove_node()

    def on_save(self):
        pos = self.physical_np.get_pos()
        return pos.getX(), pos.getY(), pos.getZ()

    def on_load(self, data):
        pos = Vec3(data[0], data[1], data[2])
        self.set_pos(pos)

    def get_np(self):
        return self.model_np

    def set_pos(self, pos):
        self.physical_np.set_pos(pos)
        if self.is_static:
            self.model_np.set_pos(pos)

    def get_pos(self):
        return self.physical_np.get_pos()
