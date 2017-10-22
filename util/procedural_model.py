#encoding: utf8

from panda3d.core import *


def create_plane(cell_size, cell_count, uv_fn):
    """
    :param uv_fn:
        uv_fn(r,c) returns (u1,v1,u2,v2)
    :return:
    """
    format = GeomVertexFormat.getV3t2()
    vdata = GeomVertexData('plane', format, Geom.UHStatic)
    vdata.setNumRows(4)
    vertex = GeomVertexWriter(vdata, 'vertex')
    texcoord = GeomVertexWriter(vdata, 'texcoord')
    prim = GeomTriangles(Geom.UHStatic)

    point_count = 0
    for r in range(cell_count):
        for c in range(cell_count):
            by, bx = r * cell_size, c * cell_size
            u1, v1, u2, v2 = uv_fn(r, c)

            vertex.addData3f(bx+0, by+0, 0)
            texcoord.addData2f(u1, v1)
            vertex.addData3f(bx+cell_size, by+0, 0)
            texcoord.addData2f(u2, v1)
            vertex.addData3f(bx+cell_size, by+cell_size, 0)
            texcoord.addData2f(u2, v2)
            vertex.addData3f(bx+0, by+cell_size, 0)
            texcoord.addData2f(u1, v2)

            prim.addVertices(point_count, point_count+1, point_count+2)
            prim.addVertices(point_count, point_count+2, point_count+3)

            point_count += 4

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode('plane_geom_node')
    node.addGeom(geom)
    return node


if __name__ == '__main__':
    from direct.showbase.ShowBase import ShowBase

    class Test(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            tile_size = 1.
            tile_count = 10
            self.np = self.render.attachNewNode(create_plane(tile_size, tile_count))
            tex = self.loader.loadTexture("assets/images/tiles/tiles.png")
            tex.set_magfilter(Texture.FT_nearest)
            print 'texture:', tex
            print 'node path:', self.np
            self.np.setTexture(tex)
            x = tile_size * tile_count * .5
            self.cam.setPos(x, x, x * 2 * 3)
            self.cam.lookAt(Vec3(x, x, 0))

    Test().run()


