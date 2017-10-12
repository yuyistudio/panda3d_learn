#encoding: utf8

from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

def test():
    format = GeomVertexFormat.getV3t2()
    vdata = GeomVertexData('plane', format, Geom.UHStatic)
    vdata.setNumRows(4)
    vertex = GeomVertexWriter(vdata, 'vertex')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    vertex.addData3f(0 ,0 ,0)
    texcoord.addData2f(0 ,0)
    vertex.addData3f(1 ,0 ,0)
    texcoord.addData2f(1 ,0)
    vertex.addData3f(1 ,1 ,0)
    texcoord.addData2f(1 ,1)
    vertex.addData3f(0, 1, 0)
    texcoord.addData2f(0, 1)

    prim = GeomTriangles(Geom.UHStatic)
    prim.addVertices(0, 1, 2)
    prim.addVertices(0, 2, 3)

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode('plane_geom_node')
    node.addGeom(geom)

    return node

class Test(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.np = self.render.attachNewNode(test())
        tex = self.loader.loadTexture("../images/logo.png")
        print 'texture:', tex
        print 'node path:', self.np
        self.np.setTexture(tex)
        self.cam.setPos(0, 0, 5)
        self.cam.lookAt(self.np)

Test().run()


