# encoding: utf8

__author__ = 'Leon'
from direct.filter.FilterManager import FilterManager
from variable.global_vars import G
from panda3d.core import Shader, Texture, Vec2
import math


class PostEffects(object):
    def __init__(self):
        manager = FilterManager(G.win, G.cam)
        tex = Texture()
        quad = manager.renderSceneInto(colortex=tex)
        quad.setShader(Shader.load("assets/shaders/post/post.sha"))
        quad.setShaderInput("color", tex)
        quad.setShaderInput("active", 2)
        self.quad = quad
        self.mgr = manager
        self.timer = 0

    def on_update(self, dt):
        self.timer += 1
        self.quad.setShaderInput('value', self.timer)  #Vec2(1.0, 1.0))


