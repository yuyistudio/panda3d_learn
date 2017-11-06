#encoding: utf8

from panda3d.core import *
from panda3d.bullet import *
from variable.global_vars import G
import config


class PhysicsWorld(object):
    """
    object hierarchy:
        render
            physical_node (with physical_node_geom)
                visual_node (model / actor)

    trigger hierarchy:
        model node
            trigger_box (ghost node)
    """
    instance = None
    MASS_IFINITE = 0

    def __init__(self, debug=False):
        if PhysicsWorld.instance:
            raise RuntimeError("duplicated physics world")
        PhysicsWorld.instance = self
        self.use_wrapper = False  # TODO 为什么设置为True会非常卡？
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        if debug:
            debugNode = BulletDebugNode("debug_bullet")
            self.world.setDebugNode(debugNode)
            #debugNode.showWireframe(True)
            debugNp = G.render.attachNewNode(debugNode)
            debugNp.show()

    def get_world(self):
        return self.world

    def remove_collider(self, physics_np):
        self.world.remove_rigid_body(physics_np.node())

    def get_bounding_size(self, np, scale=1):
        if not isinstance(scale, list):
            scale = [scale] * 3
        bb = np.getTightBounds()  # calulcate bounds before any rotation or scale
        dx, dy, dz = abs(bb[0].getX() - bb[1].getX()) * scale[0], \
                     abs(bb[0].getY() - bb[1].getY()) * scale[1], \
                     abs(bb[0].getZ() - bb[1].getZ()) * scale[2]
        return Vec3(dx, dy, dz)

    def get_cylinder_shape(self, box_np, scale=1.):
        bbox = self.get_bounding_size(box_np, scale)
        shape = BulletCylinderShape(max(bbox[0], bbox[1]) * .5, bbox[2], Z_up)
        return shape, bbox

    def get_static_body(self, name, bit_mask, mass):
        body = BulletRigidBodyNode(name)
        body.setMass(mass)
        if not mass:
            body.set_static(True)
        body.setIntoCollideMask(bit_mask)
        return body

    def add_body(self, body):
        self.world.attach_rigid_body(body)

    def remove_body(self, body):
        self.world.remove_rigid_body(body)

    def add_cylinder_collider(self, box_np, mass=0, bit_mask=config.BIT_MASK_OBJECT, reparent=False, scale=1.):
        shape, bbox = self.get_cylinder_shape(box_np, scale)
        body = self.get_static_body('name', bit_mask, mass)
        body.add_shape(shape, TransformState.makePos(Point3(0, 0, bbox[2] * .5)))
        np = G.render.attachNewNode(body)
        np.setName("physical_cylinder")
        if reparent:
            box_np.reparentTo(np)
        self.world.attach_rigid_body(body)
        return np, bbox

    def addBoxCollider(self, box_np, mass, bit_mask=config.BIT_MASK_OBJECT, reparent=False, scale=1.):
        bbox = self.get_bounding_size(box_np, scale)
        shape = BulletBoxShape(bbox * .5)
        body = BulletRigidBodyNode('xx_box_shapes')
        body.setMass(mass)
        body.addShape(shape, TransformState.makePos(Point3(0, 0, bbox[2] * .5)))
        body.set_static(True)
        body.setIntoCollideMask(bit_mask)

        self.world.attachRigidBody(body)

        np = G.render.attachNewNode(body)
        np.setName("physical_box")
        body.setPythonTag("instance", np)
        np.setPos(box_np.getPos())

        if reparent:
            box_np.reparentTo(np)  # to sync the transform automatically
        return NodePath(np), bbox * .5

    def add_player_controller(self, view_np, bit_mask):
        height = 3.3
        radius = 0.6
        shape = BulletCapsuleShape(radius, height - 2 * radius, ZUp)
        player_node = BulletCharacterControllerNode(shape, 0.4, 'Player')
        player_np = G.render.attach_new_node(player_node)
        player_np.setCollideMask(bit_mask)
        if view_np:
            view_np.reparent_to(player_np)
            view_np.set_pos(Vec3(0, 0, height * -.5))
        self.world.attachCharacter(player_np.node())
        return player_np

    def addBoxTrigger(self, box_np, bit_mask):
        if config.SHOW_BOUNDS:
            box_np.showTightBounds()

        bb = box_np.getTightBounds()  # calulcate bounds before any rotation or scale
        dx, dy, dz = abs(bb[0].getX() - bb[1].getX()),\
                     abs(bb[0].getY() - bb[1].getY()),\
                     abs(bb[0].getZ() - bb[1].getZ())

        half_size = Vec3(dx/2, dy/2, dz/2)
        shape = BulletBoxShape(half_size)
        node = BulletGhostNode('trigger_box_shapes')
        node.addShape(shape)
        node.setIntoCollideMask(bit_mask)
        self.world.attachGhost(node)

        np = box_np.attachNewNode(node)
        np.setName("rigger_box")
        pos = Point3((bb[1].getX() + bb[0].getX()) / 2 - box_np.getX(),
                     (bb[1].getY() + bb[0].getY()) / 2 - box_np.getY(),
                     (bb[1].getZ() + bb[0].getZ()) / 2 - box_np.getZ())
        np.setPos(pos)
        return np

    def set_collider_enabled(self, np, enabled):
        node = np.node()
        if enabled:
            if isinstance(node, BulletRigidBodyNode):
                self.world.attach_rigid_body(node)
            else:
                self.world.attach_character(node)
        else:
            if isinstance(node, BulletRigidBodyNode):
                self.world.remove_rigid_body(node)
            else:
                self.world.remove_character(node)

    def addGround(self, friction=0.1):
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('physical_ground_shapes')
        node.addShape(shape)
        node.setFriction(friction)
        node.setIntoCollideMask(config.BIT_MASK_GROUND)
        np = G.render.attachNewNode(node)
        np.setName("physical_ground")  # if unset, take the name of its node
        np.setPos(0, 0, 0)
        self.world.attachRigidBody(node)
        return np

    def on_update(self, dt):
        self.world.do_physics(dt)

    def mouseHit(self, distance=1000):
        mn = G.mouseWatcherNode
        if not mn.hasMouse():
            return []
        render = G.render

        # Get from/to points from _mouse click
        pMouse = mn.getMouse()
        pFrom = Point3()
        pTo = Point3()
        G.camLens.extrude(pMouse, pFrom, pTo)
        pFrom = render.getRelativePoint(G.cam, pFrom)
        pTo = render.getRelativePoint(G.cam, pTo)
        pTo = pFrom + (pTo - pFrom) .normalized() * distance

        result = self.world.rayTestAll(pFrom, pTo, config.BIT_MASK_MOUSE)
        return result.getHits() or []
