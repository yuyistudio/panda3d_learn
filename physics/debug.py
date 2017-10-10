import direct.directbase.DirectStart
from panda3d.core import Vec3
from panda3d.bullet import *

base.cam.setPos(10, -30, 20)
base.cam.lookAt(0, 0, 5)

# World
world = BulletWorld()
world.setGravity(Vec3(0, 0, -9.81))

debugNode = BulletDebugNode("debug_bullet")
world.setDebugNode(debugNode)
debugNode.showWireframe(True)
debugNp = render.attachNewNode(debugNode)
debugNp.show()

# Plane
shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
node = BulletRigidBodyNode('Ground')
node.addShape(shape)
np = render.attachNewNode(node)
np.setPos(0, 0, -2)
world.attachRigidBody(node)

# Boxes
shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
nodes = []
for i in range(10):
    node = BulletRigidBodyNode('Box')
    nodes.append(node)
    node.setMass(1.0)
    node.addShape(shape)
    np = render.attachNewNode(node)
    np.setPos(0, 0, 2 + i * 2)
    world.attachRigidBody(node)


# Update
def update(task):
    dt = globalClock.getDt()
    world.doPhysics(dt)
    return task.cont


def space():
    nodes[0].setLinearVelocity(Vec3(2,2,2))
base.accept("space", space)
taskMgr.add(update, 'update')
run()