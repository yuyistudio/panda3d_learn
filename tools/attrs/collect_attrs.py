# encoding: utf8

"""
从配合中收集所有属性，并生成c#代码
"""

import json
import sys

valid_keys = set('id category factors effect detailed_desc exclusive'.split())

# 收集所有属性
attrs = eval(open('attributes.json').read())
all_factors = {}
for attr in attrs:
    all_factors.update(attr.get('factors', {}))
    for k in attr:
        if k not in valid_keys:
            print('invalid key: %s, %s', k, attr)
            sys.exit(1)

# 收集默认值
default_file = 'default_attrs.json'
default_js = json.loads(open(default_file).read())
invalid_keys = set(default_js.keys()) - set(all_factors.keys())
for invalid_key in invalid_keys:
    del default_js[invalid_key]
all_factors.update(default_js)

# 保存数据
data = json.dumps(all_factors, indent=4)
fout = open(default_file, 'w')
fout.write(data)
fout.close()

# 生成代码
fout = open('gen/attrs_cs_code', 'w')
for factor_name, factor_value in all_factors.iteritems():
    fout.write('public float %s = %.2ff;\n' % (factor_name, factor_value))
fout.close()

# 生成属性值列表
fout = open('gen/factor_values', 'w')
all_values = {}
for fname, fvalue in all_factors.iteritems():
    all_values[fname] = set([fvalue])
for attr in attrs:
    factors = attr.get('factors', {})
    for fname, fvalue in factors.iteritems():
        all_values[fname].add(fvalue)
for fname, fvalues in all_values.iteritems():
    fout.write('%s\t%s\n' % (fname, '|'.join([str(v) for v in fvalues])))
fout.close()

    


