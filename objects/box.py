#encoding: utf8
import variable
from util import trigger

def create(pos):
    loader = variable.show_base.loader
    box = loader.loadModel("blender/box.egg")
    box.setName("box")
    box.setPos(pos)
    box.reparentTo(variable.show_base.render)
    physical_np = variable.show_base.physics_world.addBoxCollider(box, mass=1, bit_mask=variable.BIT_MASK_OBJECT)
    physical_np.setTag("type", "box")
    return physical_np
