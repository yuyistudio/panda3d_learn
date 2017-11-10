# encoding: utf8

import sys

"""
通过字符界面展示地图生成结果.
例如编写 xx.py 文件, 测试命令为:
    python display.py xx.py
xx.py可以包含如下属性:
    required:
        generator 包含get(r,c)方法的地图生成器类
    optional:
        见 supported_attrs 的定义.
"""

sign_star = '☆'
sign_rect = '❐'

default_config = {
    None: ' ',
    'empty': ' ',
    'wall': sign_rect,
    'path': '#',
    'room': '+',
}


def display(generator, config, r, c, w=50, h=50):
    for ri in range(r, r + h):
        for ci in range(c, c + w):
            info = generator.get(ri, ci)
            sign = config[info]
            sys.stdout.write('%s ' % sign)
        sys.stdout.write('\n')

if __name__ == '__main__':
    fname = sys.argv[1]
    fname = fname.replace('.py', '')
    mod = __import__(fname)
    supported_attrs = {
        'generator': None,
        'display_config': default_config,
        'start_r': 0,
        'start_c': 0,
    }
    for attr, default_value in supported_attrs.iteritems():
        if not hasattr(mod, attr):
            setattr(mod, attr, default_value)
    display(mod.generator(), mod.display_config, mod.start_r, mod.start_c)
