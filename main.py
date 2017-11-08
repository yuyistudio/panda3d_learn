#encoding: utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')
from panda3d.core import load_prc_file
load_prc_file("./config.prc")
from variable.global_vars import G
from common import game_states, config_manager, spawner, resource_manager, context, post_effects
from assets.map_generators.perlin import PerlinMapGenerator
import gui_system
from hero import create
from panda3d.core import *
from storage_system import storage_manager
from objects import ground, box, lights
from util import states, log
from operation import operation
from direct.filter.CommonFilters import CommonFilters


class Game(object):
    def __init__(self):
        log.process('setting font')

        log.process('creating managers')
        G.storage_mgr = storage_manager.StorageManager()
        G.storage_mgr.load()

        G.post_effects = None
        def turn_on():
            G.post_effects = post_effects.PostEffects()
        G.accept('x', turn_on)

        G.res_mgr = resource_manager.ResourceManager()
        G.spawner = spawner.Spawner()

        G.config_mgr = config_manager.ConfigManager()
        G.config_mgr.register_map_config('perlin', PerlinMapGenerator)
        G.config_mgr.register_tile_config('default', 'assets/images/tiles/tiles.json')

        G.state_mgr = states.StatesManager("menu.menu")
        G.state_mgr.add_state(game_states.MainMenuState())
        G.state_mgr.add_state(game_states.GamePlayState())
        G.state_mgr.add_state(game_states.GamePauseState())

        G.gui_mgr = gui_system.GUIManager()
        G.operation = operation.Operation(None)
        G.context = context.Context()

        log.process("entering main loop")
        G.accept('f1', self._render_analysis)

        G.taskMgr.add(self.main_loop, name="main_loop")
        G.run()
        log.process("main loop finished")

    def _render_analysis(self):
        G.render.analyze()

    def main_loop(self, task):
        dt = G.taskMgr.globalClock.getDt()
        G.physics_world.on_update(dt)
        G.state_mgr.on_update(dt)
        if G.post_effects:
            G.post_effects.on_update(dt)
        return task.cont

Game()
