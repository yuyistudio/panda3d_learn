#encoding: utf8

import centermenu
import inventory_gui
from variable.global_vars import G
from mouse_info import MouseGUI


class GUIManager(object):
    def __init__(self):
        self._inventory = None
        self._main_menu = None
        self._game_menu = None
        self._mouse = MouseGUI()
        G.schedule(self.onUpdate, 'mouse_gui_update')
        self._event_handler = {}
        self._mouse_on = False

    def is_mouse_on_gui(self):
        return self._inventory.is_hover()

    def _menu_click_handler(self, event_name, idx, button):
        if not self._event_handler or button != 'mouse1':
            return
        self._emit_event(event_name)

    def _emit_event(self, event_name, **kwargs):
        handler = self._event_handler.get(event_name)
        if handler:
            handler(**kwargs)

    def get_mouse_gui(self):
        return self._mouse

    def set_event_handler(self, event, handler):
        self._event_handler[event] = handler

    def create_inventory(self):
        self._inventory = inventory_gui.InventoryGUI()

    def set_inventory_cb(self, click_cb, hover_cb):
        self._inventory.set_user_cb(hover_cb, click_cb)

    def set_bag_item(self, idx, image_path, user_data, count=0):
        self._inventory.set_bag_item(idx, image_path, user_data, count)

    def set_equipments_item(self, idx, image_path, user_data, count=0):
        self._inventory.set_equipments_item(idx, image_path, user_data, count)

    def set_item_bar_item(self, idx, image_path, user_data, count=0):
        self._inventory.set_item_bar_item(idx, image_path, user_data, count)

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
            item_width=1.2,
            item_height=.4,
            events=[
                "game_menu.continue",
                "game_menu.save",
                "game_menu.exit",
            ])

    def create_main_menu(self):
        self._main_menu = centermenu.CenterMenu([
            "继续",
            "new game",
            "settings",
            "credits",
            "exit",
        ],
            self._menu_click_handler,
            item_width=1.2,
            item_height=.4,
            events=[
                "main_menu.continue",
                "main_menu.new",
                "main_menu.settings",
                "main_menu.credits",
                "main_menu.exit",
            ])

    def onUpdate(self):
        self._mouse.onUpdate()
