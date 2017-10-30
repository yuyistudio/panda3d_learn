# encoding: utf8

__author__ = 'Leon'


from variable.global_vars import G
from panda3d.bullet import *
from panda3d.core import *

world = BulletWorld()
world.setGravity(Vec3(0, 0, -9.81))

if False:
    debugNode = BulletDebugNode("debug_bullet")
    world.setDebugNode(debugNode)
    debugNode.showWireframe(True)
    debugNp = G.render.attachNewNode(debugNode)
    debugNp.show()

shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
node = BulletRigidBodyNode('physical_ground_shapes')
node.addShape(shape)
node.setFriction(1)
node.setIntoCollideMask(1)
np = G.render.attachNewNode(node)
np.setName("physical_ground")  # if unset, take the name of its node
np.setPos(0, 0, 0)
world.attachRigidBody(node)

body_count = 50

def test1():

    for i in range(body_count):
        body = BulletRigidBodyNode('physical_box_shapes')
        body.setMass(1)
        body.set_static(True)
        body.set_deactivation_enabled(True)
        body.set_deactivation_time(0.1)
        body.setIntoCollideMask(1)
        world.attachRigidBody(body)

        for j in range(body_count):
            shape = BulletBoxShape(Vec3(1, 1, 1))
            x = i*2
            y = j*2
            z = 5
            body.addShape(shape, TransformState.makePos(Point3(x, y, z)))

            np = G.render.attachNewNode(body)
            np.setName("physical_box")
            np.setPos(Vec3(0, 0, 0))

def test2():

    for i in range(body_count):
        for j in range(body_count):
            body = BulletRigidBodyNode('physical_box_shapes')
            body.setMass(0)
            body.set_static(True)
            body.set_deactivation_enabled(True)
            body.setIntoCollideMask(1)

            world.remove_rigid_body(body)  # generates a warning
            world.attachRigidBody(body)

            shape = BulletBoxShape(Vec3(1, 1, 1))
            x = i * 2
            y = j * 2
            z = 5
            body.addShape(shape, TransformState.makePos(Point3(0, 0, 0)))

            np = G.render.attachNewNode(body)
            np.setName("physical_box")
            np.setPos(Vec3(x, y, z))

test2()

def up(task):
    dt = G.taskMgr.globalClock.getDt()
    world.do_physics(dt, 1)
    return task.cont
G.taskMgr.add(up, 'physics')
pos = 130
G.cam.set_pos(pos, pos, pos)
G.cam.look_at(0, 0, 0)
G.enableMouse()
G.run()
