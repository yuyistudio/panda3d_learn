#encoding: utf8

import light
from variable.global_vars import G


def create():
    render = G.render
    light.init(render)
    dir_light = light.add_directional(render)
    amb_light = light.add_ambient(render)
    G.cameraSelection = 0
    G.lightSelection = 0
