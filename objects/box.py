#encoding: utf8

from variable.global_vars import G
import config

def create(pos):
    loader = G.loader
    box = loader.loadModel("blender/box.egg")
    box.setName("box")
    box.setPos(pos)
    box.reparentTo(G.render)
    physical_np = G.physics_world.addBoxCollider(box, mass=1, bit_mask=config.BIT_MASK_OBJECT)
    physical_np.setTag("type", "box")
    return physical_np
