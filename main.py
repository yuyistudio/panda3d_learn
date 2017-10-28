#encoding: utf8

from common import game_states, config_manager, spawner, resource_manager, context
from assets.map_generators.perlin import PerlinMapGenerator
import gui_system
from hero import create
from panda3d.core import *
from panda3d.core import loadPrcFile
from storage_system import storage_manager
from objects import ground, box, lights
from util import states, log
from variable.global_vars import G
from operation import operation
loadPrcFile("./config.prc")


class Game(object):
    def __init__(self):
        log.process('creating game instance')
        log.process('creating managers')
        G.storage_mgr = storage_manager.StorageManager()
        G.storage_mgr.load()

        G.spawner = spawner.Spawner()

        G.res_mgr = resource_manager.ResourceManager()

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
        G.taskMgr.add(self.main_loop, name="main_loop")
        G.run()
        log.process("main loop finished")

    def main_loop(self, task):
        dt = G.taskMgr.globalClock.getDt()
        G.physics_world.on_update(dt)
        G.state_mgr.on_update(dt)
        return task.cont


Game()
