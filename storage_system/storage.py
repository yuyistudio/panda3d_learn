# encoding: utf8

import json
import logging
import os

SLOT_DATA_KEY = '__slot__'
SCENES_KEY = '__scene__'
MGR_INFO_KEY = '__mgr__'

PREFIX = './storage_data'
FILE_NAME_TEST = os.path.join(PREFIX, 'test.txt')
FILE_NAME_GLOBAL = os.path.join(PREFIX, 'global.json')
FILE_NAME_CONFIG = os.path.join(PREFIX, 'config.json')
PATTERN_SLOT_STORAGE = os.path.join(PREFIX, 'slot_%s.json')
PATTERN_SCENE_STORAGE = os.path.join(PREFIX, 'slot_%s_scene_%s.json')


def save_json(filename, data):
    """
    返回是否成功固化了数据.
    :param filename:
    :param data:
    :return:
    """
    try:
        with open(filename, 'w') as fout:
            pass
            json.dump(data, fout)
        logging.info("storage saved: %s", filename)
        return True
    except Exception, e:
        logging.error("failed to save json to file `%s`, exception `%s`", filename, e)
    return False


def load_json(filename):
    """
    载入以前固化的数据并返回, 或者None.
    :param filename:
    :return:
    """
    try:
        data = json.loads(open(filename, 'r').read())
        return data
    except Exception, e:
        logging.error("failed to load file %s, exception `%s`", filename, e)
        return False


class Scene(object):
    def __init__(self, slot_name, name):
        self._slot_name = slot_name
        self._name = name
        self._data = {}
        self._loaded = False

    def __str__(self):
        return '[slot:%s|scene:%s]' % (self._slot_name, self._name)

    def set(self, k, v):
        self._data[k] = v

    def get(self, k, must_exist=False):
        if must_exist:
            return self._data[k]
        return self._data.get(k)

    def _get_filename(self):
        return PATTERN_SCENE_STORAGE % (self._slot_name, self._name)

    def save(self):
        return save_json(self._get_filename(), self._data)

    def load(self):
        self._loaded = True
        self._data = load_json(self._get_filename())
        if self._data:
            return True
        self._data = {}
        return False


class Slot(object):
    def __init__(self, slot_name):
        self._name = slot_name
        self._slot_data = {}
        self._scenes = {}
        self._current_scene_name = None

    def set(self, k, v):
        self._slot_data[k] = v

    def get(self, k, must_exist=False):
        if must_exist:
            return self._slot_data[k]
        return self._slot_data.get(k)

    def get_scene(self, k):
        """
        获取不到时，返回None.
        :param k:
        :return:
        """
        return self._scenes.get(k)

    def get_current_scene(self):
        if self._current_scene_name:
            return self.get_scene(self._current_scene_name)
        return None

    def create_scene(self, k):
        """
        创建新的Scene，并设置为当前Scene。
        :param k:
        :return:
        """
        scene = self._scenes.get(k)
        assert not scene
        scene = Scene(self._name, k)
        self._scenes[k] = scene
        self._current_scene_name = k
        return scene

    def switch_to_scene(self, scene_name):
        """
        检查是否存在scene。如果存在，则切换过去；否则，新建并切换过去。
        :param scene_name:
        :return: 参数指定的scene实例。
        """
        if not scene_name in self._scenes:
            self.create_scene(scene_name)
        else:
            self.set_current_name(scene_name)
        return self.get_current_scene()

    def set_current_name(self, scene_name):
        self._current_scene_name = scene_name

    def save(self):
        self._slot_data[MGR_INFO_KEY] = {
            'scene_names': self._scenes.keys(),
            'current': self._current_scene_name,
        }
        return save_json(PATTERN_SLOT_STORAGE % self._name, self._slot_data)

    def load(self):
        file_name = PATTERN_SLOT_STORAGE % self._name
        self._slot_data = load_json(file_name) or {}
        if not self._slot_data:
            return False
        self._current_scene_name = self._slot_data.get(MGR_INFO_KEY, {}).get('current', None)
        for scene_name in self._slot_data.get(MGR_INFO_KEY, {}).get('scene_names', []):
            self._scenes[scene_name] = Scene(self._name, scene_name)
