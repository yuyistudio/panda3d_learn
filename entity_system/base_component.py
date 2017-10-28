#encoding: utf8


from panda3d.core import Vec3


# If there's nothing to be saved, then return NO_STORAGE flag, rather than None.
# If on_save() forgets to return its data, then None is returned,
# thus we can identify this error immediately.
NO_STORAGE_FLAG = "__NO_STORAE__"


class BaseComponent(object):
    def __init__(self):
        self._entity_weak_ref = None

    def on_start(self):
        pass

    def on_inspect(self):
        pass

    def support_inspect(self):
        return self.on_inspect != BaseComponent.on_inspect

    def on_update(self, dt):
        """
        :param dt: In seconds. There's no garentee about how much time dt is, maybe 1 minute, 1 hour or even 1 year.
        :return: True if the item this component belonged to should be removed, otherwise None of False.
        """
        pass

    def set_enabled(self, enabled):
        """
        在游戏世界不再生效.
        :return:
        """
        pass

    def destroy(self):
        """
        如果该组件申请了一堆资源，则应该在这里进行释放。
        :return:
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

    def get_entity(self):
        return self._entity_weak_ref()

    def destroy(self):
        pass

    def on_left_click(self):
        pass

    def on_right_click(self):
        pass

    def on_wheel(self, amount):
        pass

    def on_key(self, key):
        pass

    def allow_action(self, tool, key_type):
        """
        返回是否可以执行该动作
        :param tool:
        :param key_type:
        :return:
        """
        return True

    def do_action(self, tool, key_type):
        """
        返回是否执行成功
        :param tool:
        :param key_type:
        :return:
        """
        return False
