#encoding: utf8

"""
the class,whose name is started with `Item`, will be used as ItemComponent.
"""

NO_STORAGE = "__NO_STORAE__"

class BaseItemComponent(object):
    def __init__(self):
        pass

    def on_update(self, dt):
        pass

    def on_save(self):
        return NO_STORAGE

    def on_load(self, data):
        """
        :param data: the value returned by onSave
        :return:
        """
        pass

    def on_left_click(self):
        pass

    def on_right_click(self):
        pass

    def on_wheel(self, amount):
        pass

    def on_key(self, key):
        pass

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
    def __init__(self, config):
        BaseItemComponent.__init__(self)
        max_count = config["max_count"]
        self._max_count = max_count
        self._count = max_count

    def get_count(self):
        return self._count

    def get_max_count(self):
        return self._max_count

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
    def __init__(self, config):
        _SingleCustomValue.__init__(self, Nutrition(config["food"], config["sanity"]))

    def get_nutrition(self):
        return self.get_value()


class SingleValueMergeable(BaseItemComponent):
    def __init__(self, max_value):
        BaseItemComponent.__init__(self)
        self._value = max_value
        self._max_value = max_value

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


class ItemPerishable(SingleValueMergeable):
    def __init__(self, config):
        SingleValueMergeable.__init__(config.get("time", 80))


