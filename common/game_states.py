# encoding: utf8

__author__ = 'Leon'

from util.states import BaseGameState
from variable.global_vars import G
from common import game_manager, spawner
from panda3d.core import Vec3


class MainMenuState(BaseGameState):
    def __init__(self):
        BaseGameState.__init__(self, "menu.menu")

    def on_enter(self, last_name):
        G.storage_mgr.load()
        G.gui_mgr.create_main_menu()
        G.gui_mgr.set_event_handler('main_menu.new', self._start_new_game)

    @staticmethod
    def _start_new_game():
        G.state_mgr.push('game.play')

    def on_pushed(self, next_name):
        G.gui_mgr.set_main_menu_visible(False)

    def on_popped(self, last_name):
        G.gui_mgr.set_main_menu_visible(True)


class GamePlayState(BaseGameState):
    def __init__(self):
        BaseGameState.__init__(self, "game.play")

    def on_enter(self, last_name):
        if not getattr(G, 'spawner', ''):
            G.spawner = spawner.Spawner()
        G.game_mgr = game_manager.GameManager()
        from util import draw
        draw.segment(0, 0, 1, 3, 0, 1)
        draw.segment(0, 0, 1, 0, 3, 1)


    def on_update(self, dt):
        G.game_mgr.on_update(dt)

        # camera control
        G.cam.set_pos(G.game_mgr.hero.getNP().get_pos() + Vec3(0, -20, 20))
        G.cam.look_at(G.game_mgr.hero.getNP())


class GamePauseState(BaseGameState):
    def __init__(self):
        BaseGameState.__init__(self, "game.pause")
