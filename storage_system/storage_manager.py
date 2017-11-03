# encoding: utf8


"""
存储游戏信息.
一个进程中, StorageManager为单例.
存储分为Global/Slot/Scene三级结构.
    1. Global存储整个游戏的信息
    2. Slot存储一个存档的信息
    3. Scene存储一个Slot内的一个场景的信息
"""


from storage import *


SLOT_KEY = '__slots__'
CONFIG_KEY = '__config__'
GLOBAL_KEY = '__global__'


class StorageManager(object):
    def __init__(self):
        self._global = {}
        self._config = {}
        self._slots = {}

    @staticmethod
    def check_permission():
        if not save_json(FILE_NAME_TEST, 'data'):
            return False
        if load_json(FILE_NAME_TEST) != 'data':
            return False
        return True

    def set_global(self, k, v):
        self._global[k] = v

    def get_global(self, k, default_vaue=None):
        return self._global.get(k, default_vaue)

    def set_config(self, k, v):
        self._config[k] = v

    def get_config(self, k, default_value=None):
        return self._config.get(k, default_value)

    def get_slot(self, k, must_exist=False):
        slot = self._slots.get(k)
        if must_exist:
            assert slot, 'slot(%s) not found' % k
        return slot

    def get_or_create_slot_entry(self, k):
        """
        获取slot. 不存在时新建.
        :param k:
        :return:
        """
        k = str(k)
        slot = self._slots.get(k)
        if not slot:
            slot = Slot(k)
            self._slots[k] = slot
        return slot

    def save_config(self):
        """
        存储配置到磁盘. 修改配置后执行该逻辑.
        :return: 是否存储成功.
        """
        return save_json(FILE_NAME_CONFIG, self._config)

    def save_global(self):
        """
        全局信息, 例如游玩时长, 死亡次数.
        存储全局信息到磁盘. 修改全局量后执行该逻辑.
        :return: 是否存储成功.
        """
        self.set_global(MGR_INFO_KEY, {
            'slot_names': self._slots.keys(),
        })
        return save_json(FILE_NAME_GLOBAL, self._global)

    def save_slots_entry(self):
        """
        存储slot的索引等信息到磁盘. 不存储实际的场景数据.
        新建一个slot时应该执行该逻辑, 来保存对新slot的引用.
        :return:
        """
        self.save_global()

    def load(self):
        """
        载入配置和全局信息.
        Warning: Slot信息需要额外调用 load_slot 进行载入!
        :return:
        """
        self._config = load_json(FILE_NAME_CONFIG) or self._config
        self._global = load_json(FILE_NAME_GLOBAL) or self._global
        for slot_name in self._global.get(MGR_INFO_KEY, {}).get('slot_names', []):
            self._slots[slot_name] = Slot(slot_name)



import unittest
import logging

class StorageTest(unittest.TestCase):
    def test_storage(self):
        sm = StorageManager()
        self.assertTrue(sm.check_permission())

        sm.load()  # 看下会不会panic
        sm.set_global('die_number', 99)
        self.assertEqual(sm.save_global(), True)
        sm.set_config('window_size', '800x600')
        self.assertEqual(sm.save_config(), True)

        sm = StorageManager()
        sm.load()
        self.assertEqual(sm.get_global('die_number'), 99)
        self.assertEqual(sm.get_config('window_size'), '800x600')

        slot = sm.get_or_create_slot_entry('1')
        sm.save_slots_entry()
        self.assertTrue(slot)
        slot.load()

        slot.set('mode', 'survival')
        scene = slot.get_or_create_scene_entry('main_land')
        slot.save()
        scene.set('objects', [1, 2, 3])
        scene.save()

        sm = StorageManager()
        sm.load()

        slot = sm.get_or_create_slot_entry('1')
        slot.load()
        self.assertEqual(slot.get('mode'), 'survival')

        scene = slot.get_or_create_scene_entry('main_land')
        slot.save()

        scene.load()
        self.assertEqual(scene.get('objects'), [1, 2, 3])

        scene2 = slot.get_or_create_scene_entry('underwater_world')
        scene2.set('objects', 'null')
        scene2.save()
        slot.save()

        sm = StorageManager()
        sm.load()
        slot1 = sm.get_or_create_slot_entry('1')
        sm.save_slots_entry()
        slot1.load()



if __name__ == '__main__':
    unittest.main()
