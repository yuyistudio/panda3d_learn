# encoding: utf8

__author__ = 'Leon'

from util.states import BaseGameState
from variable.global_vars import G
from common import game_manager, spawner, config_manager
from panda3d.core import Vec3
from assets.map_generators.perlin import *


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
        self._main_menu_visible = False

    def on_enter(self, last_name):
        G.config_mgr = config_manager.ConfigManager()
        G.config_mgr.register_map_config('perlin', PerlinMapGenerator)
        G.config_mgr.register_tile_config('default', 'assets/images/tiles/tiles.json')

        if not getattr(G, 'spawner', ''):
            G.spawner = spawner.Spawner()

        G.game_mgr = game_manager.GameManager()
        G.gui_mgr.create_inventory()
        G.gui_mgr.create_game_menu()
        G.gui_mgr.set_game_menu_visible(self._main_menu_visible)
        G.gui_mgr.set_event_handler('game_menu.continue', self._handler_continue)
        G.gui_mgr.set_event_handler('game_menu.save', self._handler_save)
        G.gui_mgr.set_event_handler('game_menu.exit', self._handler_exit)
        G.accept("escape", self._handler_escape)

    def _handler_continue(self):
        self._main_menu_visible = False
        G.gui_mgr.set_game_menu_visible(self._main_menu_visible)

    def _handler_save(self):
        G.game_mgr.save_scene()

    def _handler_exit(self):
        self._handler_save()
        sys.exit(0)

    def _handler_escape(self):
        self._main_menu_visible = not self._main_menu_visible
        G.gui_mgr.set_game_menu_visible(self._main_menu_visible)

    def on_update(self, dt):
        G.game_mgr.on_update(dt)



class GamePauseState(BaseGameState):
    def __init__(self):
        BaseGameState.__init__(self, "game.pause")
