# encoding: utf8

__author__ = 'Leon'

from util.states import BaseState
from variable.global_vars import G
from common import game_manager, spawner, camera
from panda3d.core import Vec3
from assets.map_generators.perlin import *
from util import log


class MainMenuState(BaseState):
    def __init__(self):
        BaseState.__init__(self, "menu.menu")

    def on_enter(self, last_name):
        log.process("creating main menu")
        G.gui_mgr.create_main_menu()
        G.gui_mgr.set_event_handler('main_menu.new', self._start_new_game)

    @staticmethod
    def _start_new_game():
        G.state_mgr.push('game.play')

    def on_pushed(self, next_name):
        G.gui_mgr.set_main_menu_visible(False)

    def on_popped(self, last_name):
        G.gui_mgr.set_main_menu_visible(True)


class GamePlayState(BaseState):
    def __init__(self):
        BaseState.__init__(self, "game.play")
        self._main_menu_visible = False

    def on_leave(self, next_name):
        G.operation.set_enabled(False)

    def on_enter(self, last_name):
        log.process("creating inventory & menu")
        G.gui_mgr.create_inventory()
        G.gui_mgr.create_game_menu()
        G.gui_mgr.set_game_menu_visible(self._main_menu_visible)
        G.gui_mgr.set_event_handler('game_menu.continue', self._handler_continue)
        G.gui_mgr.set_event_handler('game_menu.save', self._handler_save)
        G.gui_mgr.set_event_handler('game_menu.exit', self._handler_exit)

        log.process("creating game manager")
        G.game_mgr = game_manager.GameManager()

        log.process('creating camera manager')
        G.camera_mgr = camera.CameraManager()

        log.process('starting operation')
        G.operation.set_enabled(True)
        G.accept("escape", self._handler_escape)

    def _handler_continue(self):
        G.operation.set_enabled(True)
        self._main_menu_visible = False
        G.gui_mgr.set_game_menu_visible(self._main_menu_visible)

    def _handler_save(self):
        G.game_mgr.save_scene()

    def _handler_exit(self):
        self._handler_save()
        sys.exit(0)

    def _handler_escape(self):
        G.operation.set_enabled(self._main_menu_visible)
        self._main_menu_visible = not self._main_menu_visible
        G.gui_mgr.set_game_menu_visible(self._main_menu_visible)

    def on_update(self, dt):
        G.operation.on_update(dt)
        G.game_mgr.on_update(dt)
        G.camera_mgr.look_at(G.operation.get_center_pos())
        G.camera_mgr.on_update(dt)


class GamePauseState(BaseState):
    def __init__(self):
        BaseState.__init__(self, "game.pause")


