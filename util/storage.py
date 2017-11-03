# encoding: utf8

__author__ = 'Leon'

import log
import json


def load_json_file(filepath):
    try:
        return json.loads(open(filepath).read())
    except Exception, e:
        log.error("failed to load json file `%s`, reason `%s`", filepath, e)
        return None
