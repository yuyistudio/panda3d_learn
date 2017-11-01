#encoding: utf8

from panda3d.core import *


def get_left_plane(h1, h2):
    return (0, 0, h1), \
           (0, 1, h1), \
           (0, 1, h2), \
           (0, 0, h2)


def get_right_plane(h1, h2):
    return (1, 1, h1), \
           (1, 0, h1), \
           (1, 0, h2), \
           (1, 1, h2)


def get_top_plane(h1, h2):
    return (0, 1, h1), \
           (1, 1, h1), \
           (1, 1, h2), \
           (0, 1, h2)


def get_bottom_plane(h1, h2):
    return (1, 0, h1), \
           (0, 0, h1), \
           (0, 0, h2), \
           (1, 0, h2)


def get_plane(h1, _):
    return (0, 0, h1), \
           (1, 0, h1), \
           (1, 1, h1), \
           (0, 1, h1)


IDX_FACE_INNER = range(4)
IDX_FACE_OUTER = (0, 3, 2, 1)
OFFSETS = ((0, -1), (0, 1), (-1, 0), (1, 0))
FNS = (get_left_plane, get_right_plane, get_bottom_plane, get_top_plane)
MIN_HEIGHT = 200


def create_plane2(cell_size, cell_count, tiled_map):
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

    height = 0
    uvs = None

    point_count = 0
    for r in range(cell_count):
        for c in range(cell_count):
            by, bx = r * cell_size, c * cell_size
            tile_info = tiled_map[(r, c)]
            if not tile_info:
                continue

            height = tile_info['level'] * cell_size

            def process_fn(fn, idx, cell_height):
                points = fn(height, height + cell_height)
                for i in idx:
                    p = points[i]
                    vertex.addData3f(bx + p[0] * cell_size, by + p[1] * cell_size, p[2])
                    texcoord.addData2f(uvs[i][0], uvs[i][1])
                prim.addVertices(point_count, point_count + 1, point_count + 2)
                prim.addVertices(point_count, point_count + 2, point_count + 3)

            # 处理地面
            u1, v1, u2, v2 = tile_info['uv']
            uvs = ((u1, v1), (u2, v1), (u2, v2), (u1, v2))
            process_fn(get_plane, IDX_FACE_INNER, 0)
            point_count += 4

            u1, v1, u2, v2 = tile_info['side_uv']
            uvs = ((u1, v1), (u2, v1), (u2, v2), (u1, v2))

            # 处理地面边缘
            if tile_info['level'] == 0:
                height = -MIN_HEIGHT
                for i in range(4):
                    offset = OFFSETS[i]
                    tile = tiled_map.get((r + offset[0], c + offset[1]))
                    if not tile or tile['level'] < -0.01:
                        process_fn(FNS[i], IDX_FACE_OUTER, MIN_HEIGHT)
                        point_count += 4

            # 处理突起
            if tile_info['level'] > 0.01:
                for i in range(4):
                    offset = OFFSETS[i]
                    tile = tiled_map.get((r + offset[0], c + offset[1]))
                    if not tile:
                        height = -MIN_HEIGHT
                        process_fn(FNS[i], IDX_FACE_OUTER, MIN_HEIGHT)
                        point_count += 4
                        height = 0
                        process_fn(FNS[i], IDX_FACE_OUTER, cell_size)
                        point_count += 4
                    elif tile['level'] < 0.01:
                        height = 0
                        process_fn(FNS[i], IDX_FACE_OUTER, cell_size)
                        point_count += 4

            # 处理凹陷
            if tile_info['level'] < -0.01:
                height = -MIN_HEIGHT
                for i in range(4):
                    offset = OFFSETS[i]
                    tile = tiled_map.get((r + offset[0], c + offset[1]))
                    if tile and tile['level'] > -0.01:
                        process_fn(FNS[i], IDX_FACE_INNER, MIN_HEIGHT)
                        point_count += 4

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode('plane_geom_node')
    node.addGeom(geom)
    return node


def create_plane(side_uv, cell_size, cell_count, tiled_map):
    """
    :param uv_fn:
        uv_fn(r,c) returns (u1,v1,u2,v2)
    :return:
    """
    u1, v1, u2, v2 = side_uv
    factor = MIN_HEIGHT / cell_size
    side_uv = ((u1, v1*factor), (u2, v1*factor), (u2, v2*factor), (u1, v2*factor))

    format = GeomVertexFormat.getV3t2()
    vdata = GeomVertexData('plane', format, Geom.UHStatic)
    vdata.setNumRows(4)
    vertex = GeomVertexWriter(vdata, 'vertex')
    texcoord = GeomVertexWriter(vdata, 'texcoord')
    prim = GeomTriangles(Geom.UHStatic)

    height = 0
    uvs = None

    point_count = 0
    for r in range(cell_count):
        for c in range(cell_count):
            by, bx = r * cell_size, c * cell_size
            tile_info = tiled_map[(r, c)]
            if not tile_info:
                continue

            def process_fn(fn, idx, cell_height):
                points = fn(height, height + cell_height)
                for i in idx:
                    p = points[i]
                    vertex.addData3f(bx + p[0] * cell_size, by + p[1] * cell_size, p[2])
                    texcoord.addData2f(uvs[i][0], uvs[i][1])
                prim.addVertices(point_count, point_count + 1, point_count + 2)
                prim.addVertices(point_count, point_count + 2, point_count + 3)

            # 处理地面
            height = 0
            u1, v1, u2, v2 = tile_info['uv']
            uvs = ((u1, v1), (u2, v1), (u2, v2), (u1, v2))
            process_fn(get_plane, IDX_FACE_INNER, 0)
            point_count += 4

            # 处理地面边缘
            uvs = side_uv
            if tile_info['level'] == 0:
                height = -MIN_HEIGHT
                for i in range(4):
                    offset = OFFSETS[i]
                    tile = tiled_map.get((r + offset[0], c + offset[1]))
                    if not tile or tile['level'] < -0.01:
                        process_fn(FNS[i], IDX_FACE_OUTER, MIN_HEIGHT)
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
            self.np.setTexture(tex)
            x = tile_size * tile_count * .5
            self.cam.setPos(x, x, x * 2 * 3)
            self.cam.lookAt(Vec3(x, x, 0))

    Test().run()


