#encoding: utf8

"""
the class,whose name is started with `Item`, will be used as ItemComponent.
"""

from entity_system.base_component import *
from config import *
from util import log
from variable.global_vars import G


class BaseItemComponent(BaseComponent):
    name = "BaseItemComponent"
    entity_type = ENTITY_TYPE_ITEM

    def __init__(self):
        BaseComponent.__init__(self)

    def on_quick_action(self, bag, idx, mouse_item):
        pass


class BaseMergeableComponent(BaseItemComponent):
    name = "mergeable"

    def __init__(self):
        BaseItemComponent.__init__(self)

    def get_merge_value(self):
        """
        for example, food freshness.
        5 apples with 0.8 freshness, merged with 4 apples with 0.9 freshness, 0.8 and 0.9 are MergeValues.
        With MergeValues and count(provided by Stackable component), we can merge two stack of items together.
        :return:
        """
        pass

    def set_merge_value(self, value):
        pass


class ItemStackable(BaseItemComponent):
    name = 'stackable'

    def __init__(self, config):
        BaseItemComponent.__init__(self)
        max_count = config.get("max_count", 10)
        self._max_count = max_count
        self._count = max_count

    def get_count(self):
        return self._count

    def get_remained_capacity(self):
        return self._max_count - self._count

    def get_max_count(self):
        return self._max_count

    def set_count(self, count):
        assert 1 <= count <= self._max_count, 'invalid stackable count %d' % count
        self._count = min(max(0, count), self._max_count)

    def change_count(self, count_delta):
        self._count += count_delta
        assert 0 <= self._count <= self._max_count, "change count from %d to %d" % (self._count - count_delta, self._count)

    def on_save(self):
        return self._count

    def on_load(self, data):
        self._count = data


class _SingleCustomValue(BaseItemComponent):
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value


class Nutrition(object):
    def __init__(self, food, sanity):
        self._food = food
        self._sanity = sanity

    def __str__(self):
        return '[food:%d|sanity:%d]' % (self._food, self._sanity)

    def on_save(self):
        return {'food': self._food, 'sanity': self._sanity}

    def on_load(self, data):
        self._food = data['food']
        self._sanity = data['sanity']


class ItemEdible(_SingleCustomValue):
    name = 'edible'

    def __init__(self, config):
        _SingleCustomValue.__init__(self, Nutrition(config.get("food", 30), config.get("sanity", 3)))

    def _get_nutrition(self):
        return self.get_value()

    def on_quick_action(self, bag, idx, mouse_item):
        log.debug("nutrition: %s", self._get_nutrition())
        ent = self.get_entity()
        if ent.use_item(1) < 1:
            ent.destroy()


class SingleValueMergeable(BaseMergeableComponent):
    def __init__(self, max_value):
        BaseMergeableComponent.__init__(self)
        self._value = max_value
        self._max_value = max_value

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def change_value(self, delta_value):
        self._value += delta_value

    def set_merge_value(self, value):
        self._value = value

    def get_merge_value(self):
        return self._value

    def on_save(self):
        return self._value

    def on_load(self, data):
        self._value = data

    def get_percentage(self):
        return 1. * self._value / self._max_value

    def set_percentage(self, percentange):
        assert 0 <= percentange <= 1, 'invalid percentange %s' % percentange
        self._value = self._max_value * percentange


class ItemPerishable(SingleValueMergeable):
    name = 'perishable'

    def __init__(self, config):
        SingleValueMergeable.__init__(self, config.get("time", 80))  # seconds

    def on_update(self, dt):
        self._value -= dt
        return self._value <= 0


class ItemEquippable(BaseItemComponent):
    name = 'equippable'

    def __init__(self, config):
        self._equip_slots = config.get('slots', [])
        self._tool_name = config.get('tool_name')
        self._tool_model = config.get('tool_model')
        assert len(self._equip_slots) == len(set(self._equip_slots)), 'duplicated slot found: `%s`' % self._equip_slots
        assert self._equip_slots, 'invalid equp slots'

    def get_slots(self):
        return self._equip_slots

    def on_equipped(self, slot_type):
        log.debug("equipped at %s", slot_type)
        if self._tool_name:
            G.game_mgr.change_equipment_model(slot_type, self._tool_name)
        elif self._tool_model:
            pass
        else:
            assert False

    def on_unequipped(self, slot_type):
        # 放下屠刀，立地成佛 ♪(＾∀＾●)ﾉ
        G.game_mgr.change_equipment_model(slot_type, None)

    def on_quick_action(self, bag, idx, mouse_item):
        if not mouse_item:
            G.game_mgr.quick_equip(bag, idx)


class ItemTool(BaseItemComponent):
    name = 'tool'

    def __init__(self, config):
        """
        action_types: {
            "pick": {"duration": 10},
            "cut": {"duration": 1},
        }
        :param config:
        :return:
        """
        self._is_hand = config.get('is_hand', False)
        BaseItemComponent.__init__(self)
        self._action_types = config.get('action_types')
        self._distance = config.get('distance')
        self._duration = config.get('use_times')
        self._endless_use = False
        if not self._duration:
            self._endless_use = True

    def is_hand(self):
        return self._is_hand

    def get_action_types(self):
        return self._action_types

    def get_distance(self):
        return self._distance

    def on_use(self, action_type):
        if self._endless_use:
            return
        # 扣除duration
        self._duration -= 1
        if self._duration < 1:
            self.get_entity().destroy()

    def on_save(self):
        return {'duration': self._duration}

    def on_load(self, data):
        self._duration = data['duration']


class ItemPlaceable(BaseItemComponent):
    name = 'placeable'

    def __init__(self, config):
        BaseItemComponent.__init__(self)
        self._target_name = config['target_name']
        self._preview_model = config['preview_model']
        self._scale = config.get('collider_size', 1.)  # scalar or list of three scalar
        self._overwrite_data = config.get('overwrite_data')
        self._shape = config.get('collider_shape', 'box')
        self._gap = config.get('place_gap', 'normal')

    def get_placement_config(self):
        return self._preview_model, self._shape, self._scale, self._gap

    def get_gen_config(self):
        return self._target_name, self._overwrite_data


