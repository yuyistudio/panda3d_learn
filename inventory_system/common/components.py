#encoding: utf8

"""
the class,whose name is started with `Item`, will be used as ItemComponent.
"""

from entity_system.base_component import BaseComponent


class BaseItemComponent(BaseComponent):
    def __init__(self):
        BaseComponent.__init__(self)


class BaseMergeableComponent(BaseItemComponent):
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
        self._count = count

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

    def on_load(self, data):
        self._value = data

    def on_save(self):
        return self._value.get_storage_data()


class Nutrition(object):
    def __init__(self, food, sanity):
        self._food = food
        self._sanity = sanity


class ItemEdible(_SingleCustomValue):
    name = 'edible'

    def __init__(self, config):
        _SingleCustomValue.__init__(self, Nutrition(config.get("food", 30), config.get("sanity", 3)))

    def get_nutrition(self):
        return self.get_value()


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
        self._equip_slots = config.get('slots', ["right_hand"])
        assert len(self._equip_slots) == len(set(self._equip_slots)), 'duplicated slot found: `%s`' % self._equip_slots
        assert self._equip_slots, 'invalid equp slots'

    def get_slots(self):
        return self._equip_slots


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
        BaseItemComponent.__init__(self)
        self._action_types = config.get('action_types')
        self._distance = config.get('distance')

    def get_action_types(self):
        return self._action_types

    def get_distance(self):
        return self._distance

    def on_use(self, action_type):
        # 扣血
        pass

class ItemDuration(BaseItemComponent):
    name = 'duration'

    def __init__(self, config):
        self._max_duration = config.get('duration', 10)
        self._duration = self._max_duration

    def change(self, delta):
        self._duration += delta
        if self._duration > self._max_duration:
            self._duration = self._max_duration
        elif self._duration < 0:
            self._duration = 0

    def is_broken(self):
        return self._duration <= 0

