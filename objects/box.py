#encoding: utf8
import variable
from util import trigger

def create(pos):
    loader = variable.show_base.loader
    box = loader.loadModel("blender/box.egg")
    box.setName("box")
    box.setPos(pos)
    box.reparentTo(variable.show_base.render)
    rigid_body = variable.show_base.physics_world.addBoxCollider(box, auto_transform=True, auto_disable=True, is_static=False)
    box.setTag("type", "box")
    # for mouse pick
    trigger.addCollisionBox(box, variable.BIT_MASK_OBJECT, "box", to_enabled=True)
    return box
