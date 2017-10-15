#encoding: utf8


# If there's nothing to be saved, then return NO_STORAGE flag, rather than None.
# If on_save() forgets to return its data, then None is returned,
# thus we can identify this error immediately.
NO_STORAGE_FLAG = "__NO_STORAE__"


class BaseComponent(object):
    def __init__(self):
        pass

    def on_update(self, dt):
        """
        :param dt: In seconds. There's no garentee about how much time dt is, maybe 1 minute, 1 hour or even 1 year.
        :return: True if the item this component belonged to should be removed, otherwise None of False.
        """
        pass

    def is_update_overwrite(self):
        return type(self).on_update != BaseComponent.on_update

    def on_save(self):
        return NO_STORAGE_FLAG

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
