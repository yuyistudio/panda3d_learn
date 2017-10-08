#encoding: utf8

import light
import variable

def create():
    render = variable.show_base.render
    light.init(render)
    dir_light = light.add_directional(render)
    amb_light = light.add_ambient(render)
    variable.show_base.cameraSelection = 0
    variable.show_base.lightSelection = 0
