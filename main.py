#encoding: utf8

from common import game_states
import gui_system
from hero import create
from panda3d.core import *
from panda3d.core import loadPrcFile
from storage_system import storage_manager
from objects import ground, box, lights
from util import states
from variable.global_vars import G
loadPrcFile("./config.prc")


class Game(object):
    def __init__(self):
        G.state_mgr = states.StatesManager("menu.menu")
        G.state_mgr.add_state(game_states.MainMenuState())
        G.state_mgr.add_state(game_states.GamePlayState())
        G.state_mgr.add_state(game_states.GamePauseState())

        G.gui_mgr = gui_system.GUIManager()

        G.storage_mgr = storage_manager.StorageManager()

        G.taskMgr.add(self.main_loop, name="main_loop")
        G.run()

    def main_loop(self, task):
        dt = G.taskMgr.globalClock.getDt()
        G.physics_world.onUpdate(dt)
        G.state_mgr.on_update(dt)
        return task.cont


Game()
