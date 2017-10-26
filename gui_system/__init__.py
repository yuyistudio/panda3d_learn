#encoding: utf8

from direct.actor.Actor import  Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
loadPrcFile("../config.prc")
from direct.gui.DirectGui import *
import centermenu
import inventory
from variable.global_vars import G
from mouse_info import MouseGUI


class GUIManager(object):
    def __init__(self):
        self._inventory = None
        self._main_menu = None
        self._game_menu = None
        self._mouse = MouseGUI()
        self._mouse.setItem(None)
        self._mouse.setText(None)
        self.item_textures = {}
        G.schedule(self.onUpdate, 'mouse_gui_update')
        self._event_handler = {}

    def _menu_click_handler(self, event_name, idx, button):
        if not self._event_handler or button != 'mouse1':
            return
        self._emit_event(event_name)

    def _emit_event(self, event_name, **kwargs):
        handler = self._event_handler.get(event_name)
        if handler:
            handler(**kwargs)

    def set_event_handler(self, event, handler):
        self._event_handler[event] = handler

    def create_inventory(self):
        self._inventory = inventory.Inventory()

    def set_main_menu_visible(self, visible):
        self._main_menu.set_visible(visible)

    def set_game_menu_visible(self, visible):
        self._game_menu.set_visible(visible)

    def create_game_menu(self):
        self._game_menu = centermenu.CenterMenu([
            "continue",
            "save",
            "exit",
        ],
            self._menu_click_handler,
            item_width=1.1,
            events=[
                "game_menu.continue",
                "game_menu.save",
                "game_menu.exit",
            ])

    def create_main_menu(self):
        self._main_menu = centermenu.CenterMenu([
            "continue",
            "new game",
            "settings",
            "credits",
            "exit",
        ],
            self._menu_click_handler,
            item_width=1.1,
            events=[
                "main_menu.continue",
                "main_menu.new",
                "main_menu.settings",
                "main_menu.credits",
                "main_menu.exit",
            ])

    def loadItemTextures(self):
        images = 'apple axe orange iron silver sapling cooking_pit cobweb'.split()
        for image_path in images:
            used_texture = G.loader.loadTexture("./assets/images/items/%s.png" % image_path)
            used_texture.set_magfilter(Texture.FT_nearest)
            self.item_textures[image_path] = used_texture

    def onUpdate(self):
        self._mouse.onUpdate()