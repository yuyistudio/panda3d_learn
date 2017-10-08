#encoding: utf8

from panda3d.core import *
import variable

def ground_segment(x1, y1, x2, y2, thickness=4, r=1, g=1, b=1, alpha=1):
    lines = LineSegs()
    lines.set_color(LColor(r, g, b, alpha))
    lines.moveTo(x1, y1, 0.5)
    lines.drawTo(x2, y2, 0.5)
    lines.setThickness(4)
    node = lines.create()
    np = NodePath(node)
    np.reparent_to(variable.show_base.render)

def segment(x1, y1, z1, x2, y2, z2, thickness=4, r=1, g=1, b=1, alpha=1):
    lines = LineSegs()
    lines.set_color(LColor(r, g, b, alpha))
    lines.moveTo(x1, y1, z1)
    lines.drawTo(x2, y2, z2)
    lines.setThickness(4)
    node = lines.create()
    np = NodePath(node)
    np.reparent_to(variable.show_base.render)

def coord_system(thickness=4, r=0, g=1, b=0, alpha=0.7):
    lines = LineSegs()
    lines.setThickness(thickness)
    size = 10
    z = 1
    lines.set_color(LColor(0, 1, 0, alpha))
    lines.moveTo(0, 0, z)
    lines.drawTo(size, 0, z)

    lines.set_color(LColor(0, 0, 0, 0.5 * alpha))
    lines.moveTo(0, 0, z)
    lines.drawTo(-size, 0, z)

    lines.set_color(LColor(1, 0, 0, alpha))
    lines.moveTo(0, 0, z)
    lines.drawTo(0, size, z)

    lines.set_color(LColor(0, 0, 0, 0.5 * alpha))
    lines.moveTo(0, 0, z)
    lines.drawTo(0, -size, z)

    node = lines.create()
    np = NodePath(node)
    np.reparent_to(variable.show_base.render)
