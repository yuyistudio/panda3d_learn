# encoding: utf8

import sys

"""
通过字符界面展示地图生成结果.
例如编写 xx.py 文件, 测试命令为:
    python display.py xx.py
xx.py可以包含如下属性:
    required:
        generator
            get(r,c) (tile_name)
            get_start_pos() (r,c)
            generate()
    optional:
        见 supported_attrs 的定义.
"""

sign_star = '☆'
sign_rect = '❐'

default_config = {
    None: ' ',
    'empty': ' ',
    'wall': sign_star,
    'path': '+',
    'room': sign_rect,
    'start_point': '@',
}


def display(generator, config, r, c, w, h):
    for ri in range(r, r + h):
        for ci in range(c, c + w):
            info = generator.get(ri, ci)
            sign = config.get(info, str(info))
            sys.stdout.write('%s ' % sign)
        sys.stdout.write('\n')

if __name__ == '__main__':
    fname = sys.argv[1]
    fname = fname.replace('.py', '')
    mod = __import__(fname)
    supported_attrs = {
        'generator': None,
        'display_config': default_config,
    }
    for attr, default_value in supported_attrs.iteritems():
        if not hasattr(mod, attr):
            setattr(mod, attr, default_value)
    w = 40
    h = 40
    generator = mod.generator()
    if hasattr(generator, 'generate'):
        generator.generate()
    center_r, center_c = generator.get_start_pos()
    # display(generator, mod.display_config, int(center_r - h / 2), int(center_c - w / 2), w, h)
    display(generator, mod.display_config, 0, 0, w, h)


