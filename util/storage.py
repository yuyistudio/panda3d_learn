# encoding: utf8

__author__ = 'Leon'

import log
import json
import os


def load_json_file(filepath):
    try:
        return json.loads(open(filepath).read())
    except Exception, e:
        log.error("failed to load json file `%s`, reason `%s`", filepath, e)
        return None


def iter_files(dirpath):
    for parent_folder, folder_names, file_names in os.walk(dirpath):
        for file_name in file_names:
            yield parent_folder, file_name

