# encoding: utf8


__author__ = 'Leon'

from panda3d.core import Fog
from variable.global_vars import G


class LinearFog(object):
    def __init__(self, r, g, b, min_dist, max_dist):
        self.fog = Fog("GlobalFog")
        self.fog.setColor(r, g, b)
        dist_base = 100 if G.debug else 0
        min_dist += dist_base
        max_dist += dist_base
        assert min_dist < max_dist
        self.fog.set_linear_range(min_dist, max_dist)
        self.fog.setLinearFallback(15, min_dist, max_dist)
        G.setBackgroundColor(r, g, b, 1)
        G.render.setFog(self.fog)
        self._enabled = True

    def switch(self):
        self._enabled = not self._enabled
        self.set_enabled(self._enabled)

    def set_enabled(self, enabled):
        self._enabled = enabled
        if enabled:
            G.render.setFog(self.fog)
        else:
            G.render.clear_fog()

    def destory(self):
        G.render.clear_fog()

